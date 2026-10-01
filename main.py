import secrets, time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from db import conn
from score import score

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

class CheckBody(BaseModel):
    siteKey: str
    signals: dict = {}

class VerifyBody(BaseModel):
    secret: str
    token: str

@app.post("/api/check")
def check(body: CheckBody, request: Request):
    site = conn.execute("SELECT * FROM sites WHERE site_key=?",
                        (body.siteKey,)).fetchone()
    if not site:
        return {"error": "bad site key"}

    ip = request.client.host
    sc, verdict, reasons = score(body.signals, ip, body.siteKey)
    token = secrets.token_hex(16)

    conn.execute(
        """INSERT INTO events (site_key, token, ip, score, verdict, reasons, created_at)
           VALUES (?,?,?,?,?,?,?)""",
        (body.siteKey, token, ip, sc, verdict, ", ".join(reasons),
         int(time.time() * 1000)),
    )
    conn.commit()
    return {"verdict": verdict, "token": token}

@app.post("/api/verify")
def verify(body: VerifyBody):
    site = conn.execute("SELECT * FROM sites WHERE secret=?",
                        (body.secret,)).fetchone()
    if not site:
        return {"ok": False}

    ev = conn.execute("SELECT * FROM events WHERE token=? AND site_key=?",
                      (body.token, site["site_key"])).fetchone()
    if not ev or ev["used"] or time.time() * 1000 - ev["created_at"] > 5 * 60 * 1000:
        return {"ok": False}

    conn.execute("UPDATE events SET used=1 WHERE id=?", (ev["id"],))
    conn.commit()
    return {"ok": ev["verdict"] in ("pass", "challenge"), "score": ev["score"]}



from fastapi.responses import HTMLResponse

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    rows = conn.execute(
        "SELECT * FROM events ORDER BY id DESC LIMIT 100").fetchall()
    html = "<h2>Events</h2><table border=1 cellpadding=6>"
    html += "<tr><th>Time</th><th>IP</th><th>Score</th><th>Verdict</th><th>Reasons</th></tr>"
    for r in rows:
        t = time.strftime("%Y-%m-%d %H:%M", time.localtime(r["created_at"] / 1000))
        html += (f"<tr><td>{t}</td><td>{r['ip']}</td><td>{r['score']}</td>"
                 f"<td>{r['verdict']}</td><td>{r['reasons']}</td></tr>")
    return html + "</table>"




app.mount("/", StaticFiles(directory="static", html=True), name="static")
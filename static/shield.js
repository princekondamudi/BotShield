(function () {
  const script = document.currentScript;
  const siteKey = script.dataset.sitekey;
  const API = script.src.replace('/shield.js', '');
  const start = Date.now();
  let mouseMoves = 0, keyPresses = 0;

  document.addEventListener('mousemove', () => mouseMoves++);
  document.addEventListener('keydown', () => keyPresses++);
  document.addEventListener('touchstart', () => mouseMoves++);

  document.querySelectorAll('form[data-shield]').forEach(form => {
    const hp = document.createElement('input');
    hp.type = 'text'; hp.name = 'website_url'; hp.tabIndex = -1;
    hp.autocomplete = 'off';
    hp.style.cssText = 'position:absolute;left:-9999px;opacity:0;';
    form.appendChild(hp);

    const tokenInput = document.createElement('input');
    tokenInput.type = 'hidden'; tokenInput.name = 'shield_token';
    form.appendChild(tokenInput);

    form.addEventListener('submit', async (e) => {
      if (tokenInput.value) return;
      e.preventDefault();

      const signals = {
        honeypot: !!hp.value,
        fillTimeMs: Date.now() - start,
        mouseMoves, keyPresses,
        webdriver: !!navigator.webdriver
      };

      try {
        const r = await fetch(API + '/api/check', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ siteKey, signals })
        });
        const data = await r.json();
        if (data.verdict === 'block') return alert('Submission blocked.');
        if (data.verdict === 'challenge') {
          if (!confirm('Quick check: are you a real person? Press OK.')) return;
        }
        tokenInput.value = data.token;
        form.submit();
      } catch (err) {
        form.submit();  // fail open
      }
    });
  });
})();
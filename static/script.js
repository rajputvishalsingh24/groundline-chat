const log = document.getElementById('log');
const emptyState = document.getElementById('emptyState');
const composer = document.getElementById('composer');
const input = document.getElementById('input');
const sendBtn = document.getElementById('sendBtn');
const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');

// Auto-grow the textarea as the user types
input.addEventListener('input', () => {
  input.style.height = 'auto';
  input.style.height = Math.min(input.scrollHeight, 140) + 'px';
});

// Enter sends, Shift+Enter makes a new line
input.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    composer.requestSubmit();
  }
});

function addMessage(role, text, isError = false) {
  if (emptyState) emptyState.remove();

  const msg = document.createElement('div');
  msg.className = `msg ${role}`;

  const bubble = document.createElement('div');
  bubble.className = 'bubble' + (isError ? ' error' : '');
  bubble.textContent = text;
  msg.appendChild(bubble);

  log.appendChild(msg);
  log.scrollTop = log.scrollHeight;
  return msg;
}

function addSources(msgEl, sources) {
  if (!sources || sources.length === 0) return;

  const wrap = document.createElement('div');
  wrap.className = 'sources';

  sources.forEach((s) => {
    const chip = document.createElement('a');
    chip.className = 'source-chip';
    chip.href = s.uri;
    chip.target = '_blank';
    chip.rel = 'noopener noreferrer';
    chip.textContent = s.title || s.uri;
    wrap.appendChild(chip);
  });

  msgEl.appendChild(wrap);
  log.scrollTop = log.scrollHeight;
}

function setThinking(isThinking) {
  statusDot.classList.toggle('thinking', isThinking);
  statusText.textContent = isThinking
    ? 'searching + thinking…'
    : 'gemini-2.5-flash · search grounding on';
  sendBtn.disabled = isThinking;
}

composer.addEventListener('submit', async (e) => {
  e.preventDefault();
  const message = input.value.trim();
  if (!message) return;

  addMessage('user', message);
  input.value = '';
  input.style.height = 'auto';
  setThinking(true);

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message }),
    });

    const data = await res.json();

    if (!res.ok) {
      addMessage('assistant', data.error || 'Something went wrong.', true);
    } else {
      const msgEl = addMessage('assistant', data.answer || '(No response text.)');
      addSources(msgEl, data.sources);
    }
  } catch (err) {
    addMessage('assistant', `Network error: ${err.message}`, true);
  } finally {
    setThinking(false);
    input.focus();
  }
});

// ── DOM References ────────────────────────────────────────────────────────────

const promptInput  = document.getElementById('prompt');
const styleSelect  = document.getElementById('style');
const numInput     = document.getElementById('num_images');
const generateBtn  = document.getElementById('generateBtn');
const statusEl     = document.getElementById('status');
const resultsEl    = document.getElementById('results');
const imageGrid    = document.getElementById('imageGrid');


// ── Event Listeners ───────────────────────────────────────────────────────────

generateBtn.addEventListener('click', handleGenerate);

document.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') handleGenerate();
});


// ── Core Handler ──────────────────────────────────────────────────────────────

async function handleGenerate() {
  const prompt    = promptInput.value.trim();
  const style     = styleSelect.value;
  const numImages = parseInt(numInput.value, 10);

  if (!validateInputs(prompt, numImages)) return;

  setLoading(true);
  clearResults();

  try {
    const images = await fetchIcons({ prompt, style, num_images: numImages });
    renderImages(images, prompt);
    setStatus(`${images.length} icon${images.length > 1 ? 's' : ''} generated.`, '');
  } catch (err) {
    setStatus(`Error: ${err.message}`, 'error');
  } finally {
    setLoading(false);
  }
}


// ── API ───────────────────────────────────────────────────────────────────────

async function fetchIcons(payload) {
  const res = await fetch('/generate-icon', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Server error ${res.status}`);
  }

  const data = await res.json();
  return data.images; // List[str] base64
}


// ── Render ────────────────────────────────────────────────────────────────────

function renderImages(images, prompt) {
  images.forEach((b64, i) => {
    const src  = `data:image/png;base64,${b64}`;
    const wrap = document.createElement('div');
    wrap.className = 'img-wrap';
    wrap.style.animationDelay = `${i * 80}ms`;

    const img  = document.createElement('img');
    img.src    = src;
    img.alt    = `${prompt} icon ${i + 1}`;

    const dlBtn     = document.createElement('button');
    dlBtn.className = 'download-btn';
    dlBtn.textContent = '↓ Save';
    dlBtn.addEventListener('click', () => downloadImage(src, `icon-${i + 1}.png`));

    wrap.appendChild(img);
    wrap.appendChild(dlBtn);
    imageGrid.appendChild(wrap);
  });

  resultsEl.hidden = false;
}

function downloadImage(src, filename) {
  const a    = document.createElement('a');
  a.href     = src;
  a.download = filename;
  a.click();
}


// ── UI Helpers ────────────────────────────────────────────────────────────────

function validateInputs(prompt, numImages) {
  if (!prompt) {
    setStatus('Enter a prompt first.', 'error');
    return false;
  }
  if (numImages < 1 || numImages > 4) {
    setStatus('Count must be between 1 and 4.', 'error');
    return false;
  }
  return true;
}

function setLoading(isLoading) {
  generateBtn.disabled = isLoading;
  if (isLoading) {
    setStatus('<span class="spinner"></span>Generating…', 'active');
  }
}

function clearResults() {
  imageGrid.innerHTML  = '';
  resultsEl.hidden     = true;
}

function setStatus(html, type) {
  statusEl.innerHTML  = html;
  statusEl.className  = type;
}
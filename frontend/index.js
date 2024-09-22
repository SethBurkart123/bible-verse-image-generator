let googleFontsAPIKey = '';

// Fetch Google Fonts API key from server
fetch('/api/google-fonts-key')
  .then(response => response.json())
  .then(data => {
    googleFontsAPIKey = data.key;
    loadGoogleFonts();
  })
  .catch(error => console.error('Error fetching Google Fonts API key:', error));

let allFonts = [];
let currentIndex = 0;

// Fetch fonts from Google Fonts API
function loadGoogleFonts() {
  if (!googleFontsAPIKey) {
    console.error('Google Fonts API key not available');
    return;
  }

  const url = `https://www.googleapis.com/webfonts/v1/webfonts?key=${googleFontsAPIKey}&sort=popularity`;

  fetch(url)
    .then(response => response.json())
    .then(data => {
      allFonts = data.items;
      populateFontDropdown('verseFont', allFonts);
      populateFontDropdown('referenceFont', allFonts);
      loadFont('Noto Serif');
      loadFont('Bebas Neue');
    })
    .catch(error => console.error('Error loading fonts:', error));
}

function populateFontDropdown(dropdownId, fonts) {
  const dropdown = document.getElementById(dropdownId);
  dropdown.innerHTML = ''; // Clear existing options

  fonts.forEach(font => {
    const option = document.createElement('option');
    option.value = font.family;
    option.textContent = font.family;
    dropdown.appendChild(option);
  });

  // Set default selected options from localStorage or default fonts
  if (dropdownId === 'verseFont') {
    dropdown.value = localStorage.getItem('verseFont') || 'Noto Serif';
  } else if (dropdownId === 'referenceFont') {
    dropdown.value = localStorage.getItem('referenceFont') || 'Bebas Neue';
  }
}

// Load selected font via WebFont Loader
function loadFont(font) {
  WebFont.load({
    google: {
      families: [font]
    }
  });
}

function saveSettings() {
  localStorage.setItem('vignetteSize', document.getElementById('vignetteSize').value);
  localStorage.setItem('vignetteIntensity', document.getElementById('vignetteIntensity').value);
  localStorage.setItem('vignetteBlur', document.getElementById('vignetteBlur').value);
  localStorage.setItem('grainIntensity', document.getElementById('grainIntensity').value);
  localStorage.setItem('grainSize', document.getElementById('grainSize').value);
  localStorage.setItem('brightness', document.getElementById('brightness').value);
  localStorage.setItem('verseFont', document.getElementById('verseFont').value);
  localStorage.setItem('referenceFont', document.getElementById('referenceFont').value);
  localStorage.setItem('verseFontSize', document.getElementById('verseFontSize').value);
  localStorage.setItem('referenceFontSize', document.getElementById('referenceFontSize').value);
  localStorage.setItem('blendMode', document.getElementById('blendMode').value);
}

function loadSettings() {
  // Load saved settings from localStorage
  document.getElementById('vignetteSize').value = localStorage.getItem('vignetteSize') || '0.8';
  document.getElementById('vignetteIntensity').value = localStorage.getItem('vignetteIntensity') || '0.59';
  document.getElementById('vignetteBlur').value = localStorage.getItem('vignetteBlur') || '98.7';
  document.getElementById('grainIntensity').value = localStorage.getItem('grainIntensity') || '0.1';
  document.getElementById('grainSize').value = localStorage.getItem('grainSize') || '1';
  document.getElementById('brightness').value = localStorage.getItem('brightness') || '1';
  document.getElementById('verseFontSize').value = localStorage.getItem('verseFontSize') || '40';
  document.getElementById('referenceFontSize').value = localStorage.getItem('referenceFontSize') || '18';
  document.getElementById('blendMode').value = localStorage.getItem('blendMode') || 'normal';

  // Load saved fonts from localStorage
  const savedVerseFont = localStorage.getItem('verseFont') || 'Noto Serif';
  const savedReferenceFont = localStorage.getItem('referenceFont') || 'Bebas Neue';

  // Set the dropdowns to the saved fonts
  document.getElementById('verseFont').value = savedVerseFont;
  document.getElementById('referenceFont').value = savedReferenceFont;

  // Apply the fonts by updating the font-family of verse and reference
  document.querySelector('.verse').style.fontFamily = savedVerseFont;
  document.querySelector('.reference').style.fontFamily = savedReferenceFont;

  // Load the fonts using the WebFont loader
  loadFont(savedVerseFont);
  loadFont(savedReferenceFont);
}

// Event listeners to save changes in localStorage
document.getElementById('vignetteSize').addEventListener('input', saveSettings);
document.getElementById('vignetteIntensity').addEventListener('input', saveSettings);
document.getElementById('vignetteBlur').addEventListener('input', saveSettings);
document.getElementById('grainIntensity').addEventListener('input', saveSettings);
document.getElementById('grainSize').addEventListener('input', saveSettings);
document.getElementById('brightness').addEventListener('input', saveSettings);
document.getElementById('verseFont').addEventListener('change', function() {
  loadFont(this.value);
  document.querySelector('.verse').style.fontFamily = this.value;
  saveSettings();
});
document.getElementById('referenceFont').addEventListener('change', function() {
  loadFont(this.value);
  document.querySelector('.reference').style.fontFamily = this.value;
  saveSettings();
});
document.getElementById('verseFontSize').addEventListener('input', function() {
  document.querySelector('.verse').style.fontSize = `${this.value}px`;
  saveSettings();
});
document.getElementById('referenceFontSize').addEventListener('input', function() {
  document.querySelector('.reference').style.fontSize = `${this.value}px`;
  saveSettings();
});
document.getElementById('blendMode').addEventListener('change', function() {
  if (material) {
    material.uniforms.blendMode.value = getBlendModeValue(this.value);
    renderScene();
  }
  saveSettings();
});

loadSettings();

let vertexShader, fragmentShader;

async function loadShaders() {
  const vertexResponse = await fetch('/shaders/vertex.glsl');
  vertexShader = await vertexResponse.text();

  const fragmentResponse = await fetch('/shaders/fragment.glsl');
  fragmentShader = await fragmentResponse.text();
}

let renderer, scene, camera, material;
let isRendering = false;

async function initThreeJS() {
  await loadShaders();
  scene = new THREE.Scene();
  camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
  renderer = new THREE.WebGLRenderer({canvas: document.getElementById('imageCanvas')});
  renderer.setSize(600, 800);
}

function createMaterial(texture) {
  return new THREE.ShaderMaterial({
    uniforms: {
      tDiffuse: { value: texture },
      vignetteSize: { value: parseFloat(localStorage.getItem('vignetteSize')) || 0.8 },
      vignetteIntensity: { value: parseFloat(localStorage.getItem('vignetteIntensity')) || 1.5 },
      vignetteBlur: { value: parseFloat(localStorage.getItem('vignetteBlur')) || 5.0 },
      grainIntensity: { value: parseFloat(localStorage.getItem('grainIntensity')) || 0.1 },
      grainSize: { value: parseFloat(localStorage.getItem('grainSize')) || 1.0 },
      brightness: { value: parseFloat(localStorage.getItem('brightness')) || 1.0 },
      resolution: { value: new THREE.Vector2(600, 800) },
      blendMode: { value: getBlendModeValue(localStorage.getItem('blendMode') || 'normal') },
    },
    vertexShader: vertexShader,
    fragmentShader: fragmentShader
  });
}

async function loadTexture(url) {
  return new Promise((resolve, reject) => {
    new THREE.TextureLoader().load(url, resolve, undefined, reject);
  });
}

// Add event listeners for sliders
document.getElementById('vignetteSize').addEventListener('input', updateUniforms);
document.getElementById('vignetteIntensity').addEventListener('input', updateUniforms);
document.getElementById('vignetteBlur').addEventListener('input', updateUniforms);
document.getElementById('grainIntensity').addEventListener('input', updateUniforms);
document.getElementById('grainSize').addEventListener('input', updateUniforms);
document.getElementById('brightness').addEventListener('input', updateUniforms);

function updateUniforms() {
  if (material) {
    material.uniforms.vignetteSize.value = parseFloat(document.getElementById('vignetteSize').value);
    material.uniforms.vignetteIntensity.value = parseFloat(document.getElementById('vignetteIntensity').value);
    material.uniforms.vignetteBlur.value = parseFloat(document.getElementById('vignetteBlur').value);
    material.uniforms.grainIntensity.value = parseFloat(document.getElementById('grainIntensity').value);
    material.uniforms.grainSize.value = parseFloat(document.getElementById('grainSize').value);
    material.uniforms.brightness.value = parseFloat(document.getElementById('brightness').value);
    material.uniforms.blendMode.value = getBlendModeValue(document.getElementById('blendMode').value);
    renderScene(); // Add this line to render the scene after updating uniforms
  }
}

// Initialize font sizes
function initializeFontSizes() {
  updateVerseFontSize();
  updateReferenceFontSize();
}

document.getElementById('verseFontSize').addEventListener('input', updateVerseFontSize);
document.getElementById('referenceFontSize').addEventListener('input', updateReferenceFontSize);

function updateVerseFontSize() {
  const fontSize = document.getElementById('verseFontSize').value;
  document.querySelector('.verse').style.fontSize = `${fontSize}px`;
}

function updateReferenceFontSize() {
  const fontSize = document.getElementById('referenceFontSize').value;
  document.querySelector('.reference').style.fontSize = `${fontSize}px`;
}

document.addEventListener('DOMContentLoaded', initializeFontSizes);

let currentVerse, currentReference;

async function loadNextVerse() {
  const response = await fetch('/next-verse');
  const data = await response.json();

  if (data.done) {
    console.log('All verses processed');
    return false;
  }

  currentVerse = data.verse;
  currentReference = data.reference;
  document.querySelector('.verse').textContent = currentVerse;
  document.querySelector('.reference').textContent = currentReference;

  // Update progress bar
  const progressBar = document.getElementById('progressBar');
  const progressText = document.getElementById('progressText');
  progressBar.value = data.progress;
  progressText.textContent = `${data.progress}%`;

  // Load new background image
  const texture = await loadTexture(data.backgroundUrl);
  
  if (!material) {
    material = createMaterial(texture);
    const plane = new THREE.PlaneBufferGeometry(2, 2.5);
    const mesh = new THREE.Mesh(plane, material);
    scene.add(mesh);
  } else {
    material.uniforms.tDiffuse.value = texture;
  }

  return true;
}

let renderRequested = false;

function renderScene() {
  if (!renderRequested) {
    renderRequested = true;
    requestAnimationFrame(() => {
      if (renderer && scene && camera) {
        renderer.render(scene, camera);
      }
      renderRequested = false;
      document.dispatchEvent(new Event('renderComplete'));
    });
  }
}

async function exportImage() {
  renderScene();
  
  await new Promise(resolve => requestAnimationFrame(resolve));

  const container = document.querySelector('.image-container');
  const canvas = await html2canvas(container, {
    scale: 2,
    useCORS: true,
    logging: false,
    width: container.offsetWidth,
    height: container.offsetHeight,
    backgroundColor: null, // This ensures transparency
    onclone: (clonedDoc) => {
      // Ensure the cloned canvas is the right size
      const clonedContainer = clonedDoc.querySelector('.image-container');
      const clonedCanvas = clonedDoc.querySelector('#imageCanvas');
      clonedCanvas.style.width = `${clonedContainer.offsetWidth}px`;
      clonedCanvas.style.height = `${clonedContainer.offsetHeight}px`;
    }
  });

  // Trim any potential white space
  const trimmedCanvas = trimCanvas(canvas);

  const imageData = trimmedCanvas.toDataURL('image/png');
  const response = await fetch('/export-image', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      imageData,
      verse: currentVerse,
      reference: currentReference,
    }),
  });
  const result = await response.json();
  return result.success;
}

// Helper function to trim any potential white space
function trimCanvas(canvas) {
  const context = canvas.getContext('2d');
  const imgData = context.getImageData(0, 0, canvas.width, canvas.height);
  const data = imgData.data;

  let top = 0, bottom = canvas.height, left = 0, right = canvas.width;

  while (top < canvas.height && isRowBlank(data, top, canvas.width)) top++;
  while (bottom > top && isRowBlank(data, bottom - 1, canvas.width)) bottom--;
  while (left < canvas.width && isColumnBlank(data, left, canvas.height, canvas.width)) left++;
  while (right > left && isColumnBlank(data, right - 1, canvas.height, canvas.width)) right--;

  const trimmed = context.getImageData(left, top, right - left, bottom - top);
  canvas.width = right - left;
  canvas.height = bottom - top;
  context.putImageData(trimmed, 0, 0);

  return canvas;
}

function isRowBlank(data, y, width) {
  for (let x = 0; x < width; x++) {
    if (data[(y * width + x) * 4 + 3] !== 0) return false;
  }
  return true;
}

function isColumnBlank(data, x, height, width) {
  for (let y = 0; y < height; y++) {
    if (data[(y * width + x) * 4 + 3] !== 0) return false;
  }
  return true;
}

async function processAllVerses() {
  const progressContainer = document.getElementById('progressContainer');
  progressContainer.style.display = 'block';

  while (await loadNextVerse()) {
    // Wait for the render to complete
    await new Promise(resolve => {
      renderScene();
      document.addEventListener('renderComplete', resolve, { once: true });
    });
    await exportImage();
  }

  progressContainer.style.display = 'none';
  console.log('All verses processed and exported');
}

const startButton = document.getElementById('startButton');

startButton.addEventListener('click', () => {
  startButton.innerHTML = 'Generating...';
  startButton.disabled = true;

  processAllVerses().then(() => {
    startButton.innerHTML = 'Generation Complete';
    startButton.disabled = false;
  });
});

// Add this new function to handle the random image button click
function handleRandomImageClick() {
  loadSampleImage();
}

// Modify the existing loadSampleImage function
async function loadSampleImage() {
  try {
    const response = await fetch('/random-background');
    const data = await response.json();
    
    if (data.backgroundUrl) {
      const texture = await loadTexture(data.backgroundUrl);
      if (!material) {
        material = createMaterial(texture);
        const plane = new THREE.PlaneBufferGeometry(2, 2.5);
        const mesh = new THREE.Mesh(plane, material);
        scene.add(mesh);
      } else {
        material.uniforms.tDiffuse.value = texture;
      }
      renderScene();
    } else {
      console.error('No background image URL received');
    }
  } catch (error) {
    console.error('Error loading random background:', error);
  }
}

// Add this code near the end of the file, after the startButton event listener
const randomImageButton = document.getElementById('randomImageButton');
randomImageButton.addEventListener('click', handleRandomImageClick);

// Initialize Three.js setup
initThreeJS().then(() => {
    loadSampleImage();
    animate();
});

// Modify the animate function
function animate() {
  requestAnimationFrame(animate);
  // Remove renderScene() from here, as we'll call it explicitly when needed
}

function getBlendModeValue(mode) {
  const modeMap = {
    'normal': 0,
    'lighten': 1,
    'screen': 2,
    'colorDodge': 3,
    'linearDodge': 4,
    'overlay': 5,
    'softLight': 6,
    'hardLight': 7
  };
  return modeMap[mode] || 0;
}
// Configuration
// const API_BASE = '/api';
const API_BASE = 'https://visual-search-ot8r.onrender.com/api';
let selectedCategory = 'all';
let selectedImage = null;

// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const preview = document.getElementById('preview');
const previewImage = document.getElementById('previewImage');
const searchBtn = document.getElementById('searchBtn');
const loading = document.getElementById('loading');
const resultsSection = document.getElementById('resultsSection');
const resultsGrid = document.getElementById('resultsGrid');
const categoryBtns = document.querySelectorAll('.category-btn');
const stats = document.getElementById('stats');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    loadStats();
});

function setupEventListeners() {
    // Category selection
    categoryBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            categoryBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            selectedCategory = btn.dataset.category;
        });
    });

    // File upload
    uploadArea.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);

    // Drag and drop
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);

    // Search
    searchBtn.addEventListener('click', performSearch);
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) processFile(file);
}

function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
}

function handleDragLeave() {
    uploadArea.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');

    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
        processFile(file);
    }
}

function processFile(file) {
    if (file.size > 10 * 1024 * 1024) {
        alert('Image size must be less than 10MB');
        return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
        selectedImage = e.target.result;
        previewImage.src = selectedImage;
        preview.classList.remove('hidden');
        searchBtn.classList.remove('hidden');
        resultsSection.classList.add('hidden');
    };
    reader.readAsDataURL(file);
}

async function performSearch() {
    if (!selectedImage) return;

    searchBtn.disabled = true;
    loading.classList.remove('hidden');
    resultsSection.classList.add('hidden');

    try {
        const response = await fetch(`${API_BASE}/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                image: selectedImage,
                category: selectedCategory,
                top_k: 10
            })
        });

        const data = await response.json();

        if (data.status === 'success') {
            displayResults(data.results);
        } else {
            alert('Search failed: ' + (data.message || 'Unknown error'));
        }
    } catch (error) {
        console.error('Search error:', error);
        alert('Failed to perform search. Please try again.');
    } finally {
        loading.classList.add('hidden');
        searchBtn.disabled = false;
    }
}

function displayResults(results) {
    resultsGrid.innerHTML = '';
    resultsSection.classList.remove('hidden');

    document.getElementById('resultCount').textContent =
        `Found ${results.length} similar animals`;

    results.forEach((result, index) => {
        console.log("Result: ", result);
        const resultDiv = document.createElement('div');
        resultDiv.className = 'result-item';
        resultDiv.style.animation = `fadeIn 0.5s ease-out ${index * 0.1}s both`;

        resultDiv.innerHTML = `
            <img src="${result.image_url}"
                 alt="${result.category}"
                 crossorigin="anonymous"
                 onerror="this.src='/static/images/256x256.jpg'"
                 >
            <div class="result-info">
                <span class="result-category ${result.category}">
                    ${result.category}
                </span>
                <div class="similarity-score">
                    ${(result.score * 100).toFixed(1)}% match
                </div>
            </div>
        `;

        resultsGrid.appendChild(resultDiv);
    });
}

async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/stats`);
        const data = await response.json();

        stats.innerHTML = `
            📊 Database: ${data.total_vectors?.toLocaleString() || 0} vectors
            <br>Usage: ${data.free_tier_usage || '0%'}
        `;
    } catch (error) {
        console.error('Failed to load stats:', error);
        stats.innerHTML = '📊 Stats unavailable';
    }
}

// Add fade-in animation
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;
document.head.appendChild(style);
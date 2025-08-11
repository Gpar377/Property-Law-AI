// Configuration
const API_BASE_URL = 'http://localhost:8001';
let currentUser = null;
let authToken = null;

// DOM Elements
const elements = {
    navMenu: document.getElementById('navMenu'),
    hamburger: document.getElementById('hamburger'),
    loginBtn: document.getElementById('loginBtn'),
    registerBtn: document.getElementById('registerBtn'),
    logoutBtn: document.getElementById('logoutBtn'),
    userMenu: document.getElementById('userMenu'),
    userName: document.getElementById('userName'),
    authModal: document.getElementById('authModal'),
    closeModal: document.getElementById('closeModal'),
    loginForm: document.getElementById('loginForm'),
    registerForm: document.getElementById('registerForm'),
    caseForm: document.getElementById('caseForm'),
    analyzeBtn: document.getElementById('analyzeBtn'),
    loadingOverlay: document.getElementById('loadingOverlay'),
    resultsSection: document.getElementById('results'),
    resultsContent: document.getElementById('resultsContent'),
    confidenceScore: document.getElementById('confidenceScore'),
    downloadPdfBtn: document.getElementById('downloadPdfBtn'),
    casesGrid: document.getElementById('casesGrid')
};

// Initialize App
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    checkAuthStatus();
});

function initializeApp() {
    // Ensure loading overlay is hidden initially
    hideLoading();
    
    // Check for stored auth token
    authToken = localStorage.getItem('authToken');
    if (authToken) {
        getCurrentUser();
    }
    
    // Load user's cases if authenticated
    if (authToken) {
        loadUserCases();
    }
}

function setupEventListeners() {
    // Navigation
    elements.hamburger.addEventListener('click', toggleMobileMenu);
    
    // Auth buttons
    elements.loginBtn.addEventListener('click', () => openAuthModal('login'));
    elements.registerBtn.addEventListener('click', () => openAuthModal('register'));
    elements.logoutBtn.addEventListener('click', logout);
    
    // Modal
    elements.closeModal.addEventListener('click', closeAuthModal);
    window.addEventListener('click', (e) => {
        if (e.target === elements.authModal) {
            closeAuthModal();
        }
    });
    
    // Auth tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const tab = e.target.dataset.tab;
            switchAuthTab(tab);
        });
    });
    
    // Auth forms
    elements.loginForm.addEventListener('submit', handleLogin);
    elements.registerForm.addEventListener('submit', handleRegister);
    
    // Case form
    elements.caseForm.addEventListener('submit', handleCaseSubmission);
    
    // PDF download
    elements.downloadPdfBtn.addEventListener('click', downloadPDF);
    
    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Navigation Functions
function toggleMobileMenu() {
    elements.navMenu.classList.toggle('active');
}

function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Authentication Functions
function openAuthModal(tab = 'login') {
    elements.authModal.style.display = 'block';
    switchAuthTab(tab);
}

function closeAuthModal() {
    elements.authModal.style.display = 'none';
}

function switchAuthTab(tab) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tab}"]`).classList.add('active');
    
    // Show/hide forms
    if (tab === 'login') {
        elements.loginForm.style.display = 'block';
        elements.registerForm.style.display = 'none';
    } else {
        elements.loginForm.style.display = 'none';
        elements.registerForm.style.display = 'block';
    }
}

async function handleLogin(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    try {
        showLoading();
        console.log('Attempting login to:', `${API_BASE_URL}/auth/login`);
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: formData.get('email'),
                password: formData.get('password')
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            authToken = data.access_token;
            localStorage.setItem('authToken', authToken);
            currentUser = data.user;
            updateAuthUI();
            closeAuthModal();
            showNotification('Login successful!', 'success');
            loadUserCases();
        } else {
            showNotification(data.detail || 'Login failed', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showNotification(`Network error: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    try {
        showLoading();
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: formData.get('name'),
                email: formData.get('email'),
                password: formData.get('password')
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification('Registration successful! Please login.', 'success');
            switchAuthTab('login');
        } else {
            showNotification(data.detail || 'Registration failed', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

async function getCurrentUser() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            currentUser = await response.json();
            updateAuthUI();
        } else {
            logout();
        }
    } catch (error) {
        console.error('Error getting current user:', error);
        logout();
    }
}

function logout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    updateAuthUI();
    elements.casesGrid.innerHTML = '';
    showNotification('Logged out successfully', 'info');
}

function updateAuthUI() {
    if (currentUser) {
        elements.loginBtn.style.display = 'none';
        elements.registerBtn.style.display = 'none';
        elements.userMenu.style.display = 'flex';
        elements.userName.textContent = currentUser.name;
    } else {
        elements.loginBtn.style.display = 'inline-flex';
        elements.registerBtn.style.display = 'inline-flex';
        elements.userMenu.style.display = 'none';
    }
}

function checkAuthStatus() {
    updateAuthUI();
}

// Case Analysis Functions
async function handleCaseSubmission(e) {
    e.preventDefault();
    
    if (!authToken) {
        showNotification('Please login to analyze cases', 'warning');
        openAuthModal('login');
        return;
    }
    
    const formData = new FormData(e.target);
    
    try {
        showLoading('Analyzing your case with AI...');
        
        const caseData = {
            title: formData.get('title'),
            case_text: formData.get('case_text'),
            dispute_type: formData.get('dispute_type')
        };
        
        console.log('Sending case data:', caseData);
        console.log('API URL:', `${API_BASE_URL}/api/analyze-case`);
        
        // Test backend connectivity first
        const testResponse = await fetch(`${API_BASE_URL}/`);
        console.log('Backend test response:', testResponse.status);
        
        const response = await fetch(`${API_BASE_URL}/api/analyze-case`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(caseData)
        });
        
        console.log('Response status:', response.status);
        
        const result = await response.json();
        console.log('Response data:', result);
        
        if (response.ok) {
            displayResults(result);
            loadUserCases(); // Refresh cases list
            showNotification('Case analysis completed!', 'success');
        } else {
            console.error('API Error:', result);
            console.error('Full error details:', JSON.stringify(result, null, 2));
            showNotification(result.detail || result.message || 'Analysis failed', 'error');
        }
    } catch (error) {
        console.error('Network error:', error);
        showNotification(`Network error: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

function displayResults(result) {
    const aiResponse = result.ai_response;
    
    // Update confidence score
    const score = aiResponse.confidence_score || 5;
    elements.confidenceScore.textContent = score;
    elements.confidenceScore.className = 'score-circle';
    
    if (score >= 7) {
        elements.confidenceScore.classList.add('score-high');
    } else if (score >= 4) {
        elements.confidenceScore.classList.add('score-medium');
    } else {
        elements.confidenceScore.classList.add('score-low');
    }
    
    // Build results HTML
    let resultsHTML = '';
    
    // Case Summary
    if (aiResponse.case_summary) {
        resultsHTML += `
            <div class="result-card fade-in">
                <h3><i class="fas fa-file-alt"></i> Case Summary</h3>
                <div class="law-item">
                    <strong>Facts:</strong> ${aiResponse.case_summary.facts}
                </div>
                <div class="law-item">
                    <strong>Claims:</strong> ${aiResponse.case_summary.claims}
                </div>
                <div class="law-item">
                    <strong>Dispute Nature:</strong> ${aiResponse.case_summary.dispute_nature}
                </div>
            </div>
        `;
    }
    
    // Legal Issues
    if (aiResponse.legal_issues && aiResponse.legal_issues.length > 0) {
        resultsHTML += `
            <div class="result-card fade-in">
                <h3><i class="fas fa-exclamation-triangle"></i> Key Legal Issues</h3>
                <ul>
                    ${aiResponse.legal_issues.map(issue => `<li>${issue}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    // Applicable Laws
    if (aiResponse.applicable_laws && aiResponse.applicable_laws.length > 0) {
        resultsHTML += `
            <div class="result-card fade-in">
                <h3><i class="fas fa-balance-scale"></i> Applicable Laws</h3>
                ${aiResponse.applicable_laws.map(law => `
                    <div class="law-item">
                        <strong>${law.law}:</strong> ${law.relevance}
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    // Strategies
    if (aiResponse.strategies) {
        resultsHTML += `
            <div class="result-card fade-in">
                <h3><i class="fas fa-chess"></i> Legal Strategies</h3>
                <div class="strategy-section">
                    ${aiResponse.strategies.plaintiff ? `
                        <div class="strategy-card">
                            <h4>For Plaintiff:</h4>
                            <ul>
                                ${aiResponse.strategies.plaintiff.map(strategy => `<li>${strategy}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                    ${aiResponse.strategies.defendant ? `
                        <div class="strategy-card">
                            <h4>For Defendant:</h4>
                            <ul>
                                ${aiResponse.strategies.defendant.map(strategy => `<li>${strategy}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    // Next Steps
    if (aiResponse.next_steps && aiResponse.next_steps.length > 0) {
        resultsHTML += `
            <div class="result-card fade-in">
                <h3><i class="fas fa-tasks"></i> Recommended Next Steps</h3>
                <ul>
                    ${aiResponse.next_steps.map(step => `<li>${step}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    // Missing Evidence
    if (aiResponse.missing_evidence && aiResponse.missing_evidence.length > 0) {
        resultsHTML += `
            <div class="result-card fade-in">
                <h3><i class="fas fa-search"></i> Missing Evidence</h3>
                <ul>
                    ${aiResponse.missing_evidence.map(evidence => `<li>${evidence}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    // Timeline and Costs
    if (aiResponse.estimated_timeline || aiResponse.estimated_costs) {
        resultsHTML += `
            <div class="result-card fade-in">
                <h3><i class="fas fa-clock"></i> Timeline & Costs</h3>
                ${aiResponse.estimated_timeline ? `
                    <div class="law-item">
                        <strong>Estimated Timeline:</strong> ${aiResponse.estimated_timeline}
                    </div>
                ` : ''}
                ${aiResponse.estimated_costs ? `
                    <div class="law-item">
                        <strong>Estimated Costs:</strong> ${aiResponse.estimated_costs}
                    </div>
                ` : ''}
            </div>
        `;
    }
    
    // Precedents
    if (aiResponse.precedents && aiResponse.precedents.length > 0) {
        resultsHTML += `
            <div class="result-card fade-in">
                <h3><i class="fas fa-book"></i> Relevant Precedents</h3>
                ${aiResponse.precedents.map(precedent => `
                    <div class="law-item">
                        <strong>${precedent.case}:</strong> ${precedent.relevance}
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    elements.resultsContent.innerHTML = resultsHTML;
    elements.resultsSection.style.display = 'block';
    
    // Store case ID for PDF download
    elements.downloadPdfBtn.dataset.caseId = result.id;
    
    // Scroll to results
    setTimeout(() => {
        elements.resultsSection.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }, 100);
}

// Cases Management
async function loadUserCases() {
    if (!authToken) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/cases`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const cases = await response.json();
            displayCases(cases);
        }
    } catch (error) {
        console.error('Error loading cases:', error);
    }
}

function displayCases(cases) {
    if (cases.length === 0) {
        elements.casesGrid.innerHTML = `
            <div class="text-center">
                <p>No cases found. <a href="#analyze" onclick="scrollToSection('analyze')">Analyze your first case</a></p>
            </div>
        `;
        return;
    }
    
    const casesHTML = cases.map(caseItem => `
        <div class="case-card fade-in">
            <h3>${caseItem.title}</h3>
            <div class="case-meta">
                <span><i class="fas fa-tag"></i> ${formatDisputeType(caseItem.dispute_type)}</span>
                <span><i class="fas fa-calendar"></i> ${formatDate(caseItem.created_at)}</span>
            </div>
            <div class="case-preview">
                ${caseItem.case_text.substring(0, 150)}...
            </div>
            <div class="case-actions">
                <button class="btn btn-outline" onclick="viewCase('${caseItem.id}')">
                    <i class="fas fa-eye"></i> View
                </button>
                <button class="btn btn-primary" onclick="downloadCasePDF('${caseItem.id}')">
                    <i class="fas fa-download"></i> PDF
                </button>
            </div>
        </div>
    `).join('');
    
    elements.casesGrid.innerHTML = casesHTML;
}

function formatDisputeType(type) {
    const types = {
        'inheritance': 'Inheritance & Partition',
        'boundary': 'Boundary Disputes',
        'mutation': 'Mutation & Title',
        'tax': 'Property Tax',
        'bbmp_bda': 'BBMP/BDA Issues',
        'other': 'Other'
    };
    return types[type] || type;
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-IN');
}

async function viewCase(caseId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/cases/${caseId}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const caseData = await response.json();
            displayResults(caseData);
        }
    } catch (error) {
        showNotification('Error loading case details', 'error');
    }
}

// PDF Functions
async function downloadPDF() {
    const caseId = elements.downloadPdfBtn.dataset.caseId;
    if (!caseId) return;
    
    await downloadCasePDF(caseId);
}

async function downloadCasePDF(caseId) {
    try {
        showLoading('Generating PDF report...');
        
        const response = await fetch(`${API_BASE_URL}/api/cases/${caseId}/pdf`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `case-report-${caseId}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            showNotification('PDF downloaded successfully!', 'success');
        } else {
            showNotification('Error generating PDF', 'error');
        }
    } catch (error) {
        showNotification('Error downloading PDF', 'error');
    } finally {
        hideLoading();
    }
}

// Utility Functions
function showLoading(message = 'Loading...') {
    elements.loadingOverlay.style.display = 'flex';
    const loadingText = elements.loadingOverlay.querySelector('p');
    if (loadingText) {
        loadingText.textContent = message;
    }
}

function hideLoading() {
    elements.loadingOverlay.style.display = 'none';
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span>${message}</span>
            <button class="notification-close">&times;</button>
        </div>
    `;
    
    // Add styles if not already added
    if (!document.querySelector('#notification-styles')) {
        const styles = document.createElement('style');
        styles.id = 'notification-styles';
        styles.textContent = `
            .notification {
                position: fixed;
                top: 90px;
                right: 20px;
                padding: 15px 20px;
                border-radius: 6px;
                color: white;
                z-index: 10000;
                animation: slideIn 0.3s ease-out;
                max-width: 400px;
            }
            .notification-success { background: #27ae60; }
            .notification-error { background: #e74c3c; }
            .notification-warning { background: #f39c12; }
            .notification-info { background: #3498db; }
            .notification-content {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .notification-close {
                background: none;
                border: none;
                color: white;
                font-size: 1.2rem;
                cursor: pointer;
                margin-left: 15px;
            }
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(styles);
    }
    
    // Add to page
    document.body.appendChild(notification);
    
    // Close button functionality
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
        notification.remove();
    });
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}
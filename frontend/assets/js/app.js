// API Configuration
const API_BASE_URL = '/api';

// State management
let currentUser = null;
let cart = { items: [], subtotal: 0, total_items: 0 };
let sessionId = getCookie('session_id') || generateSessionId();

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupEventListeners();
    checkAuthStatus();
    loadCart();
    handleRouting();
});

// Router
function handleRouting() {
    const path = window.location.pathname;
    
    if (path === '/' || path === '/index.html') {
        loadProducts();
    } else if (path === '/products') {
        loadProducts();
    } else if (path.startsWith('/product/')) {
        const productId = path.split('/')[2];
        loadProductDetail(productId);
    } else if (path === '/cart') {
        showCart();
    } else if (path === '/checkout') {
        showCheckout();
    } else if (path === '/login') {
        showLogin();
    } else if (path === '/register') {
        showRegister();
    } else if (path === '/order-confirmation') {
        const orderId = new URLSearchParams(window.location.search).get('order_id');
        if (orderId) {
            showOrderConfirmation(orderId);
        } else {
            window.location.href = '/';
        }
    }
}

// Initialize App
function initializeApp() {
    // Set session cookie if not exists
    if (!getCookie('session_id')) {
        document.cookie = `session_id=${sessionId}; path=/; max-age=86400`;
    }
}

// Event Listeners
function setupEventListeners() {
    // Search toggle
    document.getElementById('searchToggle')?.addEventListener('click', toggleSearch);
    
    // Search button
    document.getElementById('searchButton')?.addEventListener('click', performSearch);
    
    // Search input (enter key)
    document.getElementById('searchInput')?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') performSearch();
    });
    
    // Sort select
    document.getElementById('sortSelect')?.addEventListener('change', performSearch);
    
    // User menu toggle
    document.getElementById('userMenuToggle')?.addEventListener('click', toggleUserMenu);
    
    // Logout link
    document.getElementById('logoutLink')?.addEventListener('click', logout);
    
    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.user-menu')) {
            document.getElementById('userDropdown')?.classList.remove('show');
        }
    });
    
    // Handle navigation links
    document.querySelectorAll('a[href]').forEach(link => {
        link.addEventListener('click', (e) => {
            const href = link.getAttribute('href');
            if (href.startsWith('/') && !href.startsWith('//')) {
                e.preventDefault();
                navigateTo(href);
            }
        });
    });
}

// Navigation
function navigateTo(path) {
    window.history.pushState({}, '', path);
    handleRouting();
}

// Toggle Search Bar
function toggleSearch() {
    const searchBar = document.getElementById('searchBar');
    searchBar.style.display = searchBar.style.display === 'none' ? 'block' : 'none';
    if (searchBar.style.display === 'block') {
        document.getElementById('searchInput').focus();
    }
}

// Perform Search (ID 586)
async function performSearch() {
    const query = document.getElementById('searchInput').value;
    const sort = document.getElementById('sortSelect').value;
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/search?q=${encodeURIComponent(query)}&sort=${sort}`);
        const data = await response.json();
        
        displaySearchResults(data);
        window.history.pushState({}, '', `/products?q=${encodeURIComponent(query)}&sort=${sort}`);
    } catch (error) {
        showToast('Error performing search', 'error');
    } finally {
        hideLoading();
    }
}

// Display Search Results
function displaySearchResults(data) {
    const mainContent = document.getElementById('mainContent');
    const template = document.getElementById('product-list-template');
    const content = template.content.cloneNode(true);
    
    const productGrid = content.getElementById('productGrid');
    
    if (data.results.length === 0) {
        productGrid.innerHTML = '<p class="no-results">No products found.</p>';
    } else {
        data.results.forEach(product => {
            const productCard = createProductCard(product);
            productGrid.appendChild(productCard);
        });
    }
    
    // Add pagination if needed
    if (data.total > data.limit) {
        const pagination = createPagination(data);
        content.getElementById('pagination').appendChild(pagination);
    }
    
    mainContent.innerHTML = '';
    mainContent.appendChild(content);
}

// Create Product Card
function createProductCard(product) {
    const card = document.createElement('a');
    card.href = `/product/${product.id}`;
    card.className = 'product-card';
    
    card.innerHTML = `
        <div class="product-card-image">
            <img src="${product.cover_image_url || '/assets/images/placeholder-cover.jpg'}" 
                 alt="${product.title}"
                 onerror="this.src='/assets/images/placeholder-cover.jpg'">
        </div>
        <div class="product-card-content">
            <h3 class="product-card-title">${escapeHtml(product.title)}</h3>
            <p class="product-card-author">${escapeHtml(product.author || 'Unknown Author')}</p>
            <p class="product-card-price">€${product.price.toFixed(2)}</p>
        </div>
    `;
    
    card.addEventListener('click', (e) => {
        e.preventDefault();
        navigateTo(`/product/${product.id}`);
    });
    
    return card;
}

// Load Products
async function loadProducts() {
    showLoading();
    
    try {
        const urlParams = new URLSearchParams(window.location.search);
        const query = urlParams.get('q') || '';
        const sort = urlParams.get('sort') || 'relevance';
        
        const response = await fetch(`${API_BASE_URL}/search?q=${encodeURIComponent(query)}&sort=${sort}`);
        const data = await response.json();
        
        displaySearchResults(data);
    } catch (error) {
        showToast('Error loading products', 'error');
    } finally {
        hideLoading();
    }
}

// Load Product Detail (ID 604, 614, 616)
async function loadProductDetail(productId) {
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/products/${productId}`);
        const product = await response.json();
        
        displayProductDetail(product);
    } catch (error) {
        showToast('Error loading product details', 'error');
        navigateTo('/products');
    } finally {
        hideLoading();
    }
}

// Display Product Detail
function displayProductDetail(product) {
    const mainContent = document.getElementById('mainContent');
    const template = document.getElementById('product-detail-template');
    const content = template.content.cloneNode(true);
    
    // Set breadcrumb
    content.getElementById('productTitleBreadcrumb').textContent = product.title;
    
    // Set product images
    content.getElementById('productCover').src = product.cover_image_url || '/assets/images/placeholder-cover.jpg';
    
    // Set product info
    content.getElementById('productTitle').textContent = product.title;
    content.getElementById('productAuthor').textContent = product.author || 'Unknown Author';
    content.getElementById('productIsbn').innerHTML = `<strong>ISBN:</strong> ${product.isbn13 || 'N/A'}`;
    content.getElementById('productPublisher').innerHTML = `<strong>Publisher:</strong> ${product.publisher || 'N/A'}`;
    
    if (product.publication_date) {
        const date = new Date(product.publication_date);
        content.getElementById('productPublicationDate').innerHTML = 
            `<strong>Published:</strong> ${date.toLocaleDateString()}`;
    }
    
    content.getElementById('productPrice').textContent = `€${product.price.toFixed(2)}`;
    content.getElementById('productDescription').innerHTML = product.description || 'No description available.';
    
    // Setup quantity controls
    const quantityInput = content.getElementById('quantity');
    content.getElementById('decreaseQty').addEventListener('click', () => {
        const current = parseInt(quantityInput.value);
        if (current > 1) quantityInput.value = current - 1;
    });
    
    content.getElementById('increaseQty').addEventListener('click', () => {
        const current = parseInt(quantityInput.value);
        if (current < 99) quantityInput.value = current + 1;
    });
    
    // Add to cart (ID 748)
    content.getElementById('addToCartBtn').addEventListener('click', async () => {
        const quantity = parseInt(quantityInput.value);
        await addToCart(product.id, quantity);
    });
    
    mainContent.innerHTML = '';
    mainContent.appendChild(content);
}

// Add to Cart (ID 748)
async function addToCart(productId, quantity = 1) {
    try {
        const response = await fetch(`${API_BASE_URL}/cart/items`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': currentUser ? `Bearer ${localStorage.getItem('token')}` : ''
            },
            body: JSON.stringify({ product_id: productId, quantity })
        });
        
        if (response.ok) {
            await loadCart();
            showToast('Item added to cart', 'success');
        } else {
            throw new Error('Failed to add to cart');
        }
    } catch (error) {
        showToast('Error adding to cart', 'error');
    }
}

// Load Cart (ID 751)
async function loadCart() {
    try {
        const response = await fetch(`${API_BASE_URL}/cart/`, {
            headers: {
                'Authorization': currentUser ? `Bearer ${localStorage.getItem('token')}` : ''
            }
        });
        
        if (response.ok) {
            cart = await response.json();
            updateCartDisplay();
        }
    } catch (error) {
        console.error('Error loading cart:', error);
    }
}

// Update Cart Display (ID 886)
function updateCartDisplay() {
    const cartCount = document.getElementById('cartCount');
    const cartTotal = document.getElementById('cartTotal');
    
    cartCount.textContent = cart.total_items > 99 ? '99+' : cart.total_items;
    cartTotal.textContent = `€${cart.subtotal.toFixed(2)}`;
}

// Show Cart (ID 751, 759, 760)
async function showCart() {
    showLoading();
    await loadCart();
    
    const mainContent = document.getElementById('mainContent');
    const template = document.getElementById('cart-template');
    const content = template.content.cloneNode(true);
    
    const cartItemsContainer = content.getElementById('cartItems');
    
    if (cart.items.length === 0) {
        cartItemsContainer.innerHTML = `
            <div class="cart-empty">
                <h2>Your cart is empty</h2>
                <p>Browse our <a href="/products">products</a> to find something you like.</p>
            </div>
        `;
    } else {
        cart.items.forEach(item => {
            const cartItem = createCartItemElement(item);
            cartItemsContainer.appendChild(cartItem);
        });
    }
    
    content.getElementById('cartSubtotal').textContent = `€${cart.subtotal.toFixed(2)}`;
    content.getElementById('cartShipping').textContent = cart.subtotal >= 50 ? '€0.00' : '€5.00';
    
    const shipping = cart.subtotal >= 50 ? 0 : 5;
    const total = cart.subtotal + shipping;
    content.getElementById('cartTotal').textContent = `€${total.toFixed(2)}`;
    
    content.getElementById('checkoutBtn').addEventListener('click', () => {
        if (cart.items.length > 0) {
            navigateTo('/checkout');
        }
    });
    
    mainContent.innerHTML = '';
    mainContent.appendChild(content);
    hideLoading();
}

// Create Cart Item Element
function createCartItemElement(item) {
    const div = document.createElement('div');
    div.className = 'cart-item';
    
    div.innerHTML = `
        <div class="cart-item-image">
            <img src="${item.product.cover_image_url || '/assets/images/placeholder-cover.jpg'}" 
                 alt="${item.product.title}"
                 onerror="this.src='/assets/images/placeholder-cover.jpg'">
        </div>
        <div class="cart-item-details">
            <a href="/product/${item.product.id}" class="cart-item-title">${escapeHtml(item.product.title)}</a>
            <p class="cart-item-author">${escapeHtml(item.product.author || 'Unknown Author')}</p>
            <p class="cart-item-price">€${item.unit_price.toFixed(2)} each</p>
        </div>
        <div class="cart-item-actions">
            <input type="number" class="cart-item-quantity" value="${item.quantity}" min="1" max="99" data-item-id="${item.id}">
            <button class="cart-item-remove" data-item-id="${item.id}" aria-label="Remove item">×</button>
        </div>
        <div class="cart-item-total">
            €${item.total_price.toFixed(2)}
        </div>
    `;
    
    // Quantity change (ID 759)
    const quantityInput = div.querySelector('.cart-item-quantity');
    quantityInput.addEventListener('change', async (e) => {
        const newQuantity = parseInt(e.target.value);
        if (newQuantity >= 1 && newQuantity <= 99) {
            await updateCartItemQuantity(e.target.dataset.itemId, newQuantity);
        } else {
            e.target.value = item.quantity;
        }
    });
    
    // Remove item (ID 760)
    const removeBtn = div.querySelector('.cart-item-remove');
    removeBtn.addEventListener('click', async () => {
        await removeFromCart(removeBtn.dataset.itemId);
    });
    
    return div;
}

// Update Cart Item Quantity (ID 759)
async function updateCartItemQuantity(itemId, quantity) {
    try {
        const response = await fetch(`${API_BASE_URL}/cart/items/${itemId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': currentUser ? `Bearer ${localStorage.getItem('token')}` : ''
            },
            body: JSON.stringify({ quantity })
        });
        
        if (response.ok) {
            await loadCart();
            showCart();
            showToast('Cart updated', 'success');
        }
    } catch (error) {
        showToast('Error updating cart', 'error');
    }
}

// Remove from Cart (ID 760)
async function removeFromCart(itemId) {
    try {
        const response = await fetch(`${API_BASE_URL}/cart/items/${itemId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': currentUser ? `Bearer ${localStorage.getItem('token')}` : ''
            }
        });
        
        if (response.ok) {
            await loadCart();
            showCart();
            showToast('Item removed from cart', 'success');
        }
    } catch (error) {
        showToast('Error removing item', 'error');
    }
}

// Show Checkout (ID 572, 932, 933)
async function showCheckout() {
    await loadCart();
    
    if (cart.items.length === 0) {
        showToast('Your cart is empty', 'warning');
        navigateTo('/cart');
        return;
    }
    
    const mainContent = document.getElementById('mainContent');
    const template = document.getElementById('checkout-template');
    const content = template.content.cloneNode(true);
    
    // Display order summary
    const checkoutItems = content.getElementById('checkoutItems');
    cart.items.forEach(item => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'order-summary-item';
        itemDiv.innerHTML = `
            <span>${escapeHtml(item.product.title)} x${item.quantity}</span>
            <span>€${item.total_price.toFixed(2)}</span>
        `;
        checkoutItems.appendChild(itemDiv);
    });
    
    const subtotal = cart.subtotal;
    const shipping = subtotal >= 50 ? 0 : 5;
    const vat = (subtotal + shipping) * 0.19;
    const total = subtotal + shipping + vat;
    
    content.getElementById('checkoutSubtotal').textContent = `€${subtotal.toFixed(2)}`;
    content.getElementById('checkoutShipping').textContent = `€${shipping.toFixed(2)}`;
    content.getElementById('checkoutVat').textContent = `€${vat.toFixed(2)}`;
    content.getElementById('checkoutTotal').textContent = `€${total.toFixed(2)}`;
    
    // Handle form submission (ID 888, 934)
    const form = content.getElementById('checkoutForm');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        await placeOrder(form, shipping);
    });
    
    mainContent.innerHTML = '';
    mainContent.appendChild(content);
}

// Place Order (ID 572, 582, 888)
async function placeOrder(form, shippingCost) {
    const formData = new FormData(form);
    
    const orderData = {
        shipping_address: {
            first_name: formData.get('firstName'),
            last_name: formData.get('lastName'),
            address_line1: formData.get('addressLine1'),
            address_line2: formData.get('addressLine2'),
            city: formData.get('city'),
            postal_code: formData.get('postalCode'),
            country: formData.get('country'),
            phone: formData.get('phone')
        },
        payment_method: formData.get('paymentMethod'),
        shipping_cost: shippingCost
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/orders/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': currentUser ? `Bearer ${localStorage.getItem('token')}` : ''
            },
            body: JSON.stringify(orderData)
        });
        
        if (response.ok) {
            const order = await response.json();
            await loadCart(); // Refresh cart (should be empty)
            navigateTo(`/order-confirmation?order_id=${order.id}`);
        } else {
            const error = await response.json();
            showToast(error.detail || 'Error placing order', 'error');
        }
    } catch (error) {
        showToast('Error placing order', 'error');
    }
}

// Show Order Confirmation (ID 582, 888, 934)
async function showOrderConfirmation(orderId) {
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/orders/${orderId}`, {
            headers: {
                'Authorization': currentUser ? `Bearer ${localStorage.getItem('token')}` : ''
            }
        });
        
        if (response.ok) {
            const order = await response.json();
            
            const mainContent = document.getElementById('mainContent');
            const template = document.getElementById('order-confirmation-template');
            const content = template.content.cloneNode(true);
            
            content.getElementById('confirmationOrderNumber').textContent = order.order_number;
            content.getElementById('confirmationEmail').textContent = currentUser?.email || 'your email';
            
            // Display order items
            const itemsContainer = content.getElementById('confirmationItems');
            order.items.forEach(item => {
                const itemDiv = document.createElement('div');
                itemDiv.className = 'order-summary-item';
                itemDiv.innerHTML = `
                    <span>${escapeHtml(item.product_title)} x${item.quantity}</span>
                    <span>€${item.total_price.toFixed(2)}</span>
                `;
                itemsContainer.appendChild(itemDiv);
            });
            
            content.getElementById('confirmationSubtotal').textContent = `€${order.subtotal.toFixed(2)}`;
            content.getElementById('confirmationShipping').textContent = `€${order.shipping_cost.toFixed(2)}`;
            content.getElementById('confirmationVat').textContent = `€${order.tax_amount.toFixed(2)}`;
            content.getElementById('confirmationTotal').textContent = `€${order.total_amount.toFixed(2)}`;
            
            mainContent.innerHTML = '';
            mainContent.appendChild(content);
            
            // Send email confirmation (ID 889)
            // This would typically be handled by the backend
        } else {
            navigateTo('/');
        }
    } catch (error) {
        showToast('Error loading order details', 'error');
        navigateTo('/');
    } finally {
        hideLoading();
    }
}

// Show Login (ID 554, 703)
function showLogin() {
    if (currentUser) {
        navigateTo('/');
        return;
    }
    
    const mainContent = document.getElementById('mainContent');
    const template = document.getElementById('login-template');
    const content = template.content.cloneNode(true);
    
    const form = content.getElementById('loginForm');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        await login(form);
    });
    
    mainContent.innerHTML = '';
    mainContent.appendChild(content);
}

// Login
async function login(form) {
    const formData = new FormData(form);
    
    try {
        const response = await fetch(`${API_BASE_URL}/users/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({
                username: formData.get('username'),
                password: formData.get('password')
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('token', data.access_token);
            await checkAuthStatus();
            showToast('Login successful', 'success');
            navigateTo('/');
        } else {
            showToast('Invalid username or password', 'error');
        }
    } catch (error) {
        showToast('Login failed', 'error');
    }
}

// Show Register (ID 528)
function showRegister() {
    if (currentUser) {
        navigateTo('/');
        return;
    }
    
    const mainContent = document.getElementById('mainContent');
    const template = document.getElementById('register-template');
    const content = template.content.cloneNode(true);
    
    const form = content.getElementById('registerForm');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        await register(form);
    });
    
    mainContent.innerHTML = '';
    mainContent.appendChild(content);
}

// Register (ID 528)
async function register(form) {
    const formData = new FormData(form);
    
    const userData = {
        email: formData.get('email'),
        username: formData.get('username'),
        full_name: formData.get('fullName'),
        password: formData.get('password')
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/users/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });
        
        if (response.ok) {
            showToast('Registration successful! Please log in.', 'success');
            navigateTo('/login');
        } else {
            const error = await response.json();
            showToast(error.detail || 'Registration failed', 'error');
        }
    } catch (error) {
        showToast('Registration failed', 'error');
    }
}

// Logout (ID 704)
async function logout(e) {
    e.preventDefault();
    
    localStorage.removeItem('token');
    currentUser = null;
    
    // Update UI
    document.getElementById('userInfo').innerHTML = `
        <span class="user-name">Guest</span>
        <span class="user-email"></span>
    `;
    document.getElementById('loginLink').style.display = 'block';
    document.getElementById('registerLink').style.display = 'block';
    document.getElementById('logoutLink').style.display = 'none';
    
    showToast('Logged out successfully', 'success');
    navigateTo('/');
}

// Check Auth Status (ID 703)
async function checkAuthStatus() {
    const token = localStorage.getItem('token');
    
    if (token) {
        try {
            const response = await fetch(`${API_BASE_URL}/users/me`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.ok) {
                currentUser = await response.json();
                
                // Update UI
                document.getElementById('userInfo').innerHTML = `
                    <span class="user-name">${escapeHtml(currentUser.full_name || currentUser.username)}</span>
                    <span class="user-email">${escapeHtml(currentUser.email)}</span>
                `;
                document.getElementById('loginLink').style.display = 'none';
                document.getElementById('registerLink').style.display = 'none';
                document.getElementById('logoutLink').style.display = 'block';
            } else {
                // Token invalid
                localStorage.removeItem('token');
            }
        } catch (error) {
            console.error('Error checking auth status:', error);
        }
    }
}

// Helper Functions
function toggleUserMenu() {
    document.getElementById('userDropdown').classList.toggle('show');
}

function showLoading() {
    const mainContent = document.getElementById('mainContent');
    mainContent.innerHTML = '<div class="loading-spinner"><div class="spinner"></div></div>';
}

function hideLoading() {
    // Loading is removed when content is rendered
}

function showToast(message, type = 'info') {
    const toastContainer = document.querySelector('.toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
        if (toastContainer.children.length === 0) {
            toastContainer.remove();
        }
    }, 3000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

function generateSessionId() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function createPagination(data) {
    const container = document.createElement('div');
    container.className = 'pagination';
    
    const totalPages = Math.ceil(data.total / data.limit);
    const currentPage = data.page;
    
    // Previous button
    const prevBtn = document.createElement('button');
    prevBtn.textContent = '←';
    prevBtn.disabled = currentPage === 1;
    prevBtn.addEventListener('click', () => {
        if (currentPage > 1) {
            const urlParams = new URLSearchParams(window.location.search);
            urlParams.set('page', currentPage - 1);
            navigateTo(`${window.location.pathname}?${urlParams.toString()}`);
        }
    });
    container.appendChild(prevBtn);
    
    // Page numbers
    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
            const pageBtn = document.createElement('button');
            pageBtn.textContent = i;
            pageBtn.className = i === currentPage ? 'active' : '';
            pageBtn.addEventListener('click', () => {
                const urlParams = new URLSearchParams(window.location.search);
                urlParams.set('page', i);
                navigateTo(`${window.location.pathname}?${urlParams.toString()}`);
            });
            container.appendChild(pageBtn);
        } else if (i === currentPage - 3 || i === currentPage + 3) {
            const ellipsis = document.createElement('span');
            ellipsis.textContent = '...';
            container.appendChild(ellipsis);
        }
    }
    
    // Next button
    const nextBtn = document.createElement('button');
    nextBtn.textContent = '→';
    nextBtn.disabled = currentPage === totalPages;
    nextBtn.addEventListener('click', () => {
        if (currentPage < totalPages) {
            const urlParams = new URLSearchParams(window.location.search);
            urlParams.set('page', currentPage + 1);
            navigateTo(`${window.location.pathname}?${urlParams.toString()}`);
        }
    });
    container.appendChild(nextBtn);
    
    return container;
}

// Handle browser back/forward
window.addEventListener('popstate', handleRouting);
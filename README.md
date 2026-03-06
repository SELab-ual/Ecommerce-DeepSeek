# Ecommerce-DeepSeek

The **First Sprint** of this Scrum project. Given the complexity and number of user stories (362 total), the first sprint should focus on establishing the **foundational infrastructure and minimal viable functionality** that allows the team to deliver a working increment.

## Sprint Goal
**"Establish the foundational architecture and deliver the minimal core e-commerce functionality to prove the end-to-end flow works."**


## Sprint 1 Coverage Summary

| Requirement ID | Feature | Implemented |
|:---|:---|:---:|
| 909 | Performance | ✅ (Gzip, caching, optimized images) |
| 945 | SSL Encryption | ✅ (Configuration ready) |
| 729 | HTTPS Access | ✅ (Configuration ready) |
| 910 | API Search Results | ✅ (Complete search API) |
| 550 | Persistent Header | ✅ (Sticky header) |
| 542 | Main Navigation | ✅ (Working navigation) |
| 171 | Mobile Header | ✅ (Responsive design) |
| 616 | Product Price | ✅ (Price display everywhere) |
| 604 | Product Cover | ✅ (Cover images with fallback) |
| 614 | Bibliographic Info | ✅ (Complete product details) |
| 586 | Listed Search Results | ✅ (Search with filtering) |
| 916 | Sort Results | ✅ (Sort by price, title) |
| 748 | Add to Cart | ✅ (Working add to cart) |
| 886 | Cart Total Display | ✅ (Real-time cart total) |
| 751 | Cart Overview | ✅ (Full cart page) |
| 759 | Change Quantity | ✅ (Quantity controls) |
| 760 | Delete from Cart | ✅ (Remove button) |
| 528 | User Registration | ✅ (Registration form) |
| 554 | User Login | ✅ (Login form) |
| 703 | Role-based Functions | ✅ (Auth system with roles) |
| 704 | User Logout | ✅ (Logout functionality) |
| 947 | Existing Data Login | ✅ (Credential verification) |
| 572 | Guest Checkout | ✅ (Guest order flow) |
| 888 | Order Confirmation | ✅ (Confirmation page) |
| 889 | Email Confirmation | ✅ (Email template ready) |
| 582 | Order Overview | ✅ (Order summary) |
| 934 | Order Summary Again | ✅ (Confirmation page) |
| 932 | Enter Address | ✅ (Address form) |
| 933 | Select Payment | ✅ (Payment method selection) |
| 771 | Payment Method | ✅ (Multiple payment options) |
| 890 | Speaking URLs | ✅ (Clean URLs) |
| 946 | Smooth Changeover | ✅ (URL structure maintained) |
| 779 | Browser Compatibility | ✅ (Cross-browser CSS) |


# How to run

```bash
# Start the application
docker-compose up --build -d

# Wait for services to be ready (30 seconds)
sleep 30

# Check logs to ensure everything is running
docker-compose logs --tail=50
```

### 2. Data Preparation (10 minutes)

```bash
# Connect to database and verify sample data
docker exec -it sprint1_db psql -U sprint1_user -d sprint1_db -c "SELECT COUNT(*) FROM products;"

# Should return 5 products

# Verify API is working
curl http://localhost:8000/health
# Expected: {"status":"healthy","database":"healthy","environment":"development"}
```


```bash
# 1. Open the application
open http://localhost

```
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Streamlit-based e-commerce analytics dashboard** that integrates WooCommerce order data with Meta (Facebook) advertising data to provide comprehensive business performance analysis. The dashboard calculates revenue, costs (COGS, shipping, payment fees, ads, tax), and estimated net profit.

**Key Features:**
- Real-time e-commerce analytics combining WooCommerce and Meta Ads data
- Secure API credential management via Streamlit secrets
- Automatic Meta API long-lived token refresh mechanism
- Cost structure analysis (COGS, shipping, payment processing, ads, tax)
- ROAS (Return on Ad Spend) tracking
- Daily profit/loss visualization
- Export functionality for detailed reports

## Architecture

### Core Files

1. **app.py** - Main Streamlit dashboard application ⭐ **PRIMARY ENTRY POINT**
   - **The only entry point for the dashboard** (dashboard.py has been removed)
   - Handles UI rendering and data visualization
   - Supports both "secure mode" (with Streamlit secrets) and "basic mode" (manual input)
   - Integrates WooCommerce and Meta API data for comprehensive analysis
   - Run with: `streamlit run app.py`

2. **config.py** - Configuration management
   - `Config` class loads API credentials from Streamlit secrets or environment variables
   - `setup_api_connections()` - Sets up API connections with fallback to manual input
   - `get_active_config()` - Returns active configuration (secrets or manual input)

3. **meta_api_enhanced.py** - Enhanced Meta Ads API client
   - `MetaAdsAPI` class with automatic token refresh capability
   - `refresh_long_lived_token()` - Exchanges short-lived tokens for long-lived ones
   - `_validate_and_refresh_token()` - Auto-refreshes tokens when nearing expiration
   - `get_ads_insights()` - Fetches ad performance data with automatic date range adjustment
   - `show_token_management()` - UI for managing Meta API tokens

4. **meta_debug.py** - Standalone debugging tool
   - Command-line script to diagnose Meta API issues
   - Useful for troubleshooting zero-spend days or API connection problems
   - Run independently with: `python meta_debug.py` (after setting credentials in file)

5. **meta_api_test.py** - Testing script for Meta API integration

### Data Flow

```
User selects date range
    ↓
Secure config loaded (config.py) or manual input
    ↓
WooCommerce API → Orders data (revenue, payment methods, shipping)
    ↓
Meta API (meta_api_enhanced.py) → Ad performance data (spend, impressions, clicks)
    ↓
Data processing & cost calculations (app.py)
    ↓
Visualization (Plotly charts) + Export (CSV downloads)
```

### Configuration Management

The app supports two modes:

**Secure Mode (Recommended for production):**
- Credentials stored in `.streamlit/secrets.toml` (not in repo)
- Auto-loads from `st.secrets.woocommerce` and `st.secrets.meta`
- Supports automatic token refresh for Meta API

**Basic Mode (Development/testing):**
- Manual input via Streamlit sidebar
- Credentials stored temporarily in `st.session_state`

Expected secrets structure:
```toml
[woocommerce]
url = "https://your-store.com"
consumer_key = "ck_xxx"
consumer_secret = "cs_xxx"

[meta]
app_id = "123456789"
app_secret = "abc123..."
account_id = "act_123456789"
long_lived_token = "EAABsb..."  # Optional, can be generated via UI
```

### Cost Calculation Logic

The dashboard calculates multiple cost components:

1. **COGS (Cost of Goods Sold)**: Revenue × COGS rate (configurable slider)
2. **Shipping Costs**: Per-order costs based on shipping method (defined in `SHIPPING_COSTS` dict)
3. **Payment Processing Fees**: Transaction amount × fee rate (defined in `PAYMENT_FEES` dict)
4. **Advertising Costs**: Direct spend from Meta API
5. **Business Tax**: Revenue × 5%

**Net Profit** = Revenue - (COGS + Shipping + Payment Fees + Ad Spend + Tax)

### Meta API Special Handling

- **Date Adjustment**: Automatically excludes today's data to avoid Meta API delays (queries up to yesterday)
- **Token Refresh**: Long-lived tokens are auto-refreshed when <7 days from expiration
- **Error Retry**: Automatic retry with token refresh on 401/403 errors
- **Debug Mode**: Optional detailed logging of API requests/responses

## Common Development Tasks

### Running the Dashboard

```bash
streamlit run app.py
```

### Installing Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- streamlit (main framework)
- pandas (data processing)
- plotly (visualization)
- requests (API calls)
- numpy (numerical operations)

### Debugging Meta API Issues

If ad spend shows zero or API errors occur:

1. Enable debug mode in sidebar ("調試設定" → "啟用調試模式")
2. Check detailed API request/response logs in the UI
3. Or run standalone debug tool:
   ```bash
   python meta_debug.py
   ```
   (Edit file first to set `ACCESS_TOKEN` and `ACCOUNT_ID`)

See `META_API_修復指南.md` for comprehensive troubleshooting guide.

### Updating Cost Parameters

Edit constants in `app.py`:
- `SHIPPING_COSTS` (line 92): Map shipping methods to costs
- `PAYMENT_FEES` (line 96): Map payment methods to fee percentages
- `TAX_RATE` (line 101): Business tax rate

### Token Management

**To generate a long-lived Meta token:**
1. Get a short-lived token from Meta Graph API Explorer
2. In the dashboard sidebar, expand "🔑 Token 管理"
3. Paste short-lived token and click "生成長期 Token"
4. Token will be stored in `st.session_state` and auto-refreshed

**Token expiration handling:**
- Tokens are automatically refreshed when <7 days remaining
- Manual refresh available via UI
- Fallback retry on API authentication errors

## Important Notes

### Security
- Never commit `.streamlit/secrets.toml` or `.env` files
- Secrets should be configured in Streamlit Cloud deployment settings
- Use secure mode for production deployments

### Meta API Limitations
- Data typically has 1-2 day delay
- Dashboard automatically adjusts date ranges to exclude today
- Long-lived tokens last ~60 days and need renewal

### Date Range Handling
- Always queries complete days only (excludes partial current day)
- Automatically adjusts invalid date ranges
- Warns users when date range is modified for data integrity

### Chinese Language
This codebase uses Traditional Chinese (繁體中文) for UI text and comments. Maintain this convention when adding features or documentation visible to end users.

## File Reference

- `app.py:163-176` - Shipping cost calculation logic
- `app.py:178-196` - Payment fee calculation logic
- `app.py:198-251` - WooCommerce data fetching
- `app.py:253-286` - Basic Meta API data fetching (fallback mode)
- `meta_api_enhanced.py:45-85` - Token refresh implementation
- `meta_api_enhanced.py:159-217` - Enhanced ads insights with debug mode
- `config.py:56-77` - Configuration validation logic
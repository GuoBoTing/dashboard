# styles.py - UI 樣式定義
"""
這個模組包含所有 Streamlit 應用的 CSS 樣式
"""

import streamlit as st


def apply_custom_css():
    """應用自定義 CSS 樣式"""
    st.markdown("""
    <style>
        .main-header {
            background: linear-gradient(90deg, #1f2937 0%, #374151 100%);
            color: white;
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
        }

        .clean-section-header {
            background: #f8fafc;
            padding: 1.2rem;
            border-radius: 8px;
            margin: 1.5rem 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .clean-section-header h2 {
            margin: 0;
            color: #1f2937;
            font-size: 1.5rem;
            font-weight: 600;
        }

        /* 隱藏所有箭頭 */
        [data-testid="metric-container"] svg,
        .metric-container svg,
        .st-emotion-cache-5znelh svg,
        .e1lfzwz56 svg,
        div[data-testid="metric-container"] > div > div > div > svg,
        .metric-container .element-container svg,
        [class*="metric"] svg,
        [class*="delta"] svg {
            display: none !important;
            visibility: hidden !important;
        }

        .secure-mode {
            background: linear-gradient(90deg, #059669 0%, #10b981 100%);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.8rem;
            display: inline-block;
            margin-bottom: 1rem;
        }

        .basic-mode {
            background: linear-gradient(90deg, #d97706 0%, #f59e0b 100%);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.8rem;
            display: inline-block;
            margin-bottom: 1rem;
        }

        .oauth-mode {
            background: linear-gradient(90deg, #1877f2 0%, #0ea5e9 100%);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.8rem;
            display: inline-block;
            margin-bottom: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)


def render_main_header(title: str, subtitle: str):
    """
    渲染主標題

    Args:
        title: 主標題文字
        subtitle: 副標題文字
    """
    st.markdown(f"""
    <div class="main-header">
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def render_section_header(title: str):
    """
    渲染區塊標題

    Args:
        title: 區塊標題文字
    """
    st.markdown(f"""
    <div class="clean-section-header">
        <h2>{title}</h2>
    </div>
    """, unsafe_allow_html=True)


def render_mode_badge(mode: str):
    """
    渲染模式徽章

    Args:
        mode: 模式名稱 ("secure", "basic", "oauth")
    """
    badges = {
        "secure": '<div class="secure-mode">🔒 安全模式：API 金鑰已加密保護</div>',
        "basic": '<div class="basic-mode">⚠️ 基本模式：請手動輸入 API 設定</div>',
        "oauth": '<div class="oauth-mode">🔐 OAuth 模式：已透過 Meta 登入認證</div>'
    }

    badge_html = badges.get(mode.lower(), badges["basic"])
    st.markdown(badge_html, unsafe_allow_html=True)
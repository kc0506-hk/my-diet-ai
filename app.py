import streamlit as st
import google.generativeai as genai

# ==========================================
# 0. 行動裝置與視覺優化設定 (非常重要)
# ==========================================
st.set_page_config(
    page_title="AI 飲食營養助手",
    page_icon="🥗",
    # 移除 layout="centered" 讓行動裝置自動填滿
    initial_sidebar_state="collapsed" # 手機上預設隱藏側邊欄，保持簡潔
)

# 自訂深色主題 CSS，強制字體變白，背景顏色根據性別切換
# 並確保在 iPhone/Android 上的 RWD 排版
def local_css(bg_color):
    st.markdown(f"""
    <style>
    /* 全局深色模式與文字變白 */
    .stApp {{
        background-color: {bg_color} !important;
        color: #FFFFFF !important;
    }}
    
    /* 強制所有文字、標題、標籤變白 */
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, .stText {{
        color: #FFFFFF !important;
    }}
    
    /* 優化輸入框在深色背景下的顯示 */
    .stTextInput>div>div>input {{
        color: #FFFFFF !important;
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }}
    
    /* 優化側邊欄顯示 */
    .sidebar .sidebar-content {{
        background-color: rgba(0, 0, 0, 0.2) !important;
        color: #FFFFFF !important;
    }}
    
    /* 聯盟行銷推薦框 (Success Box) 的文字變白 */
    .stAlert {{
        background-color: rgba(0, 255, 0, 0.1) !important;
        border: 1px solid rgba(0, 255, 0, 0.5) !important;
        color: #FFFFFF !important;
    }}
    .stAlert p {{
        color: #FFFFFF !important;
    }}

    /* 行動裝置適配 (RWD) */
    @media (max-width: 640px) {{
        .reportview-container .main .block-container {{
            padding: 1rem 0.5rem !important; /* 減少邊距 */
        }}
        h1 {{
            font-size: 1.8rem !important; /* 手機上標題變小 */
        }}
        /* 讓下拉選單和單選鈕在手機上整齊排版 */
        .row-widget.stSelectbox, .row-widget.stRadio {{
            width: 100% !important;
        }}
    }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 1. 地區與性別設定 (介面 RWD 優化)
# ==========================================
# 在手機上將性別和地區垂直排版，電腦上保持水平
col1, col2 = st.columns([1, 1])
with col1:
    st.title("🥗 我的 AI 助手")
with col2:
    st.write("") # 調整垂直對齊
    # 增加性別選擇和地區選擇
    gender = st.radio("性別：", ["男", "女"], horizontal=True)
    region = st.selectbox("地區版本：", ["香港 (廣東話)", "台灣 (國語)"])

# 根據性別選擇自訂背景顏色 (Cobalt Blue vs Magenta)
# 男：Cobalt Blue (#0047AB)
# 女：Magenta (#E11584)
custom_bg = "#0047AB" if gender == "男" else "#E11584"
local_css(custom_bg)

# ==========================================
# 2. 聯盟行銷 (Affiliate Links) 資料庫
# ==========================================
AFFILIATE_LINKS = {
    "PROTEIN": "[💪 推薦補充：iHerb 高品質乳清蛋白粉 (點擊購買)](https://hk.iherb.com/c/whey-protein?rcode=YOUR_CODE)",
    "FIBER": "[🥦 推薦補充：Amazon

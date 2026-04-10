import streamlit as st
import google.generativeai as genai

# ==========================================
# 0. 行動裝置與視覺優化設定
# ==========================================
st.set_page_config(
    page_title="AI 飲食營養助手",
    page_icon="🥗",
    initial_sidebar_state="collapsed"
)

def local_css(bg_color):
    st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color} !important; color: #FFFFFF !important; }}
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, .stText {{ color: #FFFFFF !important; }}
    .stTextInput>div>div>input {{ color: #FFFFFF !important; background-color: rgba(255, 255, 255, 0.1) !important; }}
    .stAlert {{ background-color: rgba(0, 255, 0, 0.1) !important; color: #FFFFFF !important; }}
    @media (max-width: 640px) {{
        .reportview-container .main .block-container {{ padding: 1rem 0.5rem !important; }}
        h1 {{ font-size: 1.6rem !important; }}
    }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 1. 地區與性別設定
# ==========================================
col1, col2 = st.columns([1, 1])
with col1:
    st.title("🥗 我的 AI 助手")
with col2:
    gender = st.radio("性別：", ["男", "女"], horizontal=True)
    region = st.selectbox("地區版本：", ["香港 (廣東話)", "台灣 (國語)"])

custom_bg = "#0047AB" if gender == "男" else "#E11584"
local_css(custom_bg)

# ==========================================
# 2. 聯盟行銷資料庫 (確保字串不換行)
# ==========================================
AFFILIATE_LINKS = {
    "PROTEIN": "[💪 推薦補充：iHerb 乳清蛋白粉](https://hk.iherb.com/c/whey-protein?rcode=YOUR_CODE)",
    "FIBER": "[🥦 推薦補充：Amazon 膳食纖維粉](https://www.amazon.com/dp/YOUR_LINK)",
    "VITAMIN": "[💊 推薦補充：綜合維他命](https://hk.iherb.com/c/multivitamins?rcode=YOUR_CODE)",
    "HEALTHY_SNACK": "[🥜 推薦替代：低卡無鹽堅果](https://www.amazon.com/dp/YOUR_LINK)"
}

st.sidebar.title("⚙️ 系統設定")
api_key = st.sidebar.text_input("Gemini API Key", type="password")

if api_key:
    genai.configure(api_key=api_key)

    if region == "香港 (廣東話)":
        persona = "香港註冊營養師，用廣東話口語（如：食咗啲咩、走汁）。"
        food_context = "熟悉香港茶餐廳、大牌檔文化。"
    else:
        persona = "台灣專業營養師，語氣親切自然（如：便當、滷肉飯）。"
        food_context = "熟悉台灣夜市、便當文化。"

    system_instruction = f"""你是一位專業的{persona}{food_context}
    請分析飲食內容、估算卡路里、給予1-10分健康評分及貼地建議。
    如果蛋白質不足，請在結尾加上標籤 [NEED_PROTEIN]
    如果纖維不足，請在結尾加上標籤 [NEED_FIBER]
    如果營養不均，請在結尾加上標籤 [NEED_VITAMIN]
    如果想食零食，請在結尾加上標籤 [NEED_HEALTHY_SNACK]"""

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "哈囉！今日食咗啲咩呀？"}]

    for msg in st.session_state.messages:
        clean_text = msg["content"].replace("[NEED_PROTEIN]", "").replace("[NEED_FIBER]", "").replace("[NEED_VITAMIN]", "").replace("[NEED_HEALTHY_SNACK]", "")
        with st.chat_message(msg["role"]):
            st.markdown(clean_text)

    user_input = st.chat_input("輸入你想食嘅嘢...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=system_instruction)
        chat_history = [{"role": "model" if msg["role"] == "assistant" else "user", "parts": [msg["content"]]} for msg in st.session_state.messages[:-1]]
        chat = model.start_chat(history=chat_history)

        with st.chat_message("assistant"):
            with st.spinner("分析中..."):
                response = chat.send_message(user_input)
                reply = response.text
                st.markdown(reply.replace("[NEED_PROTEIN]", "").replace("[NEED_FIBER]", "").replace("[NEED_VITAMIN]", "").replace("[NEED_HEALTHY_SNACK]", ""))
                
                if "[NEED_PROTEIN]" in reply: st.success(AFFILIATE_LINKS["PROTEIN"])
                if "[NEED_FIBER]" in reply: st.success(AFFILIATE_LINKS["FIBER"])
                if "[NEED_VITAMIN]" in reply: st.success(AFFILIATE_LINKS["VITAMIN"])
                if "[NEED_HEALTHY_SNACK]" in reply: st.success(AFFILIATE_LINKS["HEALTHY_SNACK"])

                st.session_state.messages.append({"role": "assistant", "content": reply})
else:
    st.warning("⚠️ 請在側邊欄輸入你的 Gemini API Key 以啟用服務。")

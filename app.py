import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="AI 飲食助手", page_icon="🥗", initial_sidebar_state="collapsed")

def local_css(bg_color):
    st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color} !important; color: #FFFFFF !important; }}
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, .stText {{ color: #FFFFFF !important; }}
    .stTextInput>div>div>input {{ color: #FFFFFF !important; background-color: rgba(255, 255, 255, 0.1) !important; }}
    </style>
    """, unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])
with col1:
    st.title("🥗 我的 AI 助手")
with col2:
    gender = st.radio("性別：", ["男", "女"], horizontal=True)
    region = st.selectbox("地區版本：", ["香港 (廣東話)", "台灣 (國語)"])

custom_bg = "#0047AB" if gender == "男" else "#E11584"
local_css(custom_bg)

AFFILIATE_LINKS = {
    "PROTEIN": "[💪 推薦補充：iHerb 乳清蛋白粉](https://hk.iherb.com/c/whey-protein?rcode=YOUR_CODE)",
    "FIBER": "[🥦 推薦補充：Amazon 膳食纖維粉](https://www.amazon.com/dp/YOUR_LINK)",
    "VITAMIN": "[💊 推薦補充：綜合維他命](https://hk.iherb.com/c/multivitamins?rcode=YOUR_CODE)",
    "HEALTHY_SNACK": "[🥜 推薦替代：低卡無鹽堅果](https://www.amazon.com/dp/YOUR_LINK)"
}

st.sidebar.title("⚙️ 系統設定")
api_key = st.sidebar.text_input("Gemini API Key", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # --- 自動偵測可用模型邏輯 ---
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # 優先順序：1.5-flash > 1.5-pro > 1.0-pro
        selected_model = None
        for target in ["models/gemini-1.5-flash", "models/gemini-1.5-pro", "models/gemini-pro"]:
            if target in available_models:
                selected_model = target
                break
        if not selected_model and available_models:
            selected_model = available_models[0]
        # -----------------------

        if region == "香港 (廣東話)":
            persona = "香港註冊營養師，用廣東話口語。"
        else:
            persona = "台灣專業營養師，親切自然。"

        system_instruction = f"你是一位專業的{persona}。分析飲食、估算卡路里及建議。不足蛋白質加 [NEED_PROTEIN]，不足纖維加 [NEED_FIBER]，營養不均加 [NEED_VITAMIN]，想食零食加 [NEED_HEALTHY_SNACK]"

        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": "哈囉！今日食咗啲咩呀？"}]

        for msg in st.session_state.messages:
            clean = msg["content"].replace("[NEED_PROTEIN]", "").replace("[NEED_FIBER]", "").replace("[NEED_VITAMIN]", "").replace("[NEED_HEALTHY_SNACK]", "")
            with st.chat_message(msg["role"]):
                st.markdown(clean)

        user_input = st.chat_input("輸入你想食嘅嘢...")

        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            with st.chat_message("assistant"):
                with st.spinner(f"正在使用 {selected_model} 分析中..."):
                    try:
                        model = genai.GenerativeModel(selected_model)
                        response = model.generate_content(f"{system_instruction}\n\n用戶輸入：{user_input}")
                        reply = response.text
                        
                        st.markdown(reply.replace("[NEED_PROTEIN]", "").replace("[NEED_FIBER]", "").replace("[NEED_VITAMIN]", "").replace("[NEED_HEALTHY_SNACK]", ""))
                        
                        if "[NEED_PROTEIN]" in reply: st.success(AFFILIATE_LINKS["PROTEIN"])
                        if "[NEED_FIBER]" in reply: st.success(AFFILIATE_LINKS["FIBER"])
                        if "[NEED_VITAMIN]" in reply: st.success(AFFILIATE_LINKS["VITAMIN"])
                        if "[NEED_HEALTHY_SNACK]" in reply: st.success(AFFILIATE_LINKS["HEALTHY_SNACK"])

                        st.session_state.messages.append({"role": "assistant", "content": reply})
                    except Exception as e:
                        st.error(f"分析失敗。目前選擇模型: {selected_model}。原因: {str(e)}")
                
    except Exception as e:
        st.error(f"連線失敗，請檢查 API Key。原因: {str(e)}")
else:
    st.warning("⚠️ 請在側邊欄輸入你的 Gemini API Key 以啟用服務。")

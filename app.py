import streamlit as st
import google.generativeai as genai

# 0. 基本設定
st.set_page_config(page_title="AI 飲食助手", page_icon="🥗", initial_sidebar_state="collapsed")

def local_css(bg_color):
    st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color} !important; color: #FFFFFF !important; }}
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, .stText {{ color: #FFFFFF !important; }}
    .stTextInput>div>div>input {{ color: #FFFFFF !important; background-color: rgba(255, 255, 255, 0.1) !important; }}
    </style>
    """, unsafe_allow_html=True)

# 1. 介面
col1, col2 = st.columns([1, 1])
with col1:
    st.title("🥗 我的 AI 助手")
with col2:
    gender = st.radio("性別：", ["男", "女"], horizontal=True)
    region = st.selectbox("地區版本：", ["香港 (廣東話)", "台灣 (國語)"])

custom_bg = "#0047AB" if gender == "男" else "#E11584"
local_css(custom_bg)

# 2. 連結
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
        
        # 修改點：使用 models/ 前綴確保路徑正確
        model_name = "models/gemini-1.5-flash"
        
        if region == "香港 (廣東話)":
            persona = "香港註冊營養師，用廣東話口語。"
            food_context = "熟悉香港茶餐廳文化。"
        else:
            persona = "台灣專業營養師，親切自然。"
            food_context = "熟悉台灣便當文化。"

        system_instruction = f"""你是一位專業的{persona}{food_context}
        請分析飲食內容、估算卡路里、給予1-10分評分及建議。
        若蛋白質不足，結尾加 [NEED_PROTEIN]
        若纖維不足，結尾加 [NEED_FIBER]
        若營養不均，結尾加 [NEED_VITAMIN]
        若想食零食，結尾加 [NEED_HEALTHY_SNACK]"""

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

            # 修改點：加入 Try-Except 捕捉具體錯誤
            try:
                model = genai.GenerativeModel(model_name=model_name, system_instruction=system_instruction)
                response = model.generate_content(user_input)
                reply = response.text
                
                with st.chat_message("assistant"):
                    st.markdown(reply.replace("[NEED_PROTEIN]", "").replace("[NEED_FIBER]", "").replace("[NEED_VITAMIN]", "").replace("[NEED_HEALTHY_SNACK]", ""))
                    
                    if "[NEED_PROTEIN]" in reply: st.success(AFFILIATE_LINKS["PROTEIN"])
                    if "[NEED_FIBER]" in reply: st.success(AFFILIATE_LINKS["FIBER"])
                    if "[NEED_VITAMIN]" in reply: st.success(AFFILIATE_LINKS["VITAMIN"])
                    if "[NEED_HEALTHY_SNACK]" in reply: st.success(AFFILIATE_LINKS["HEALTHY_SNACK"])

                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"AI 呼叫失敗: {str(e)}")
                
    except Exception as e:
        st.error(f"配置失敗: {str(e)}")
else:
    st.warning("⚠️ 請在側邊欄輸入你的 Gemini API Key 以啟用服務。")

import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="AI 飲食營養助手", page_icon="🥗", layout="centered")

# ==========================================
# 1. 地區與性別設定
# ==========================================
col1, col2 = st.columns([2, 1])
with col1:
    st.title("🥗 我的 AI 飲食助手")
with col2:
    st.write("") 
    region = st.selectbox("選擇地區 / 地區版本：", ["香港 (廣東話)", "台灣 (國語)"])
    gender = st.radio("你的性別：", ["男", "女"], horizontal=True)

bg_color = "#F0F8FF" if gender == "男" else "#FFF0F5"
st.markdown(f"<style>.stApp {{ background-color: {bg_color}; }}</style>", unsafe_allow_html=True)

# ==========================================
# 2. 聯盟行銷 (Affiliate Links) 資料庫
# ==========================================
# 預先設定好你自己的專屬連結
AFFILIATE_LINKS = {
    "PROTEIN": "[💪 推薦補充：iHerb 高品質乳清蛋白粉 (點擊購買)](https://hk.iherb.com/c/whey-protein?rcode=YOUR_CODE)",
    "FIBER": "[🥦 推薦補充：Amazon 膳食纖維粉 / 益生菌 (點擊購買)](https://www.amazon.com/dp/YOUR_LINK)",
    "VITAMIN": "[💊 推薦補充：綜合維他命 (點擊購買)](https://hk.iherb.com/c/multivitamins?rcode=YOUR_CODE)",
    "HEALTHY_SNACK": "[🥜 推薦替代：低卡無鹽堅果零食包 (點擊購買)](https://www.amazon.com/dp/YOUR_LINK)"
}

st.sidebar.title("⚙️ 系統設定")
api_key = st.sidebar.text_input("請輸入 Gemini API Key", type="password")

if api_key:
    genai.configure(api_key=api_key)

    # 根據地區切換 Prompt 語言同文化背景
    if region == "香港 (廣東話)":
        persona = "香港註冊營養師，全程使用道地廣東話口語（如：食咗啲咩、走汁、唔好撈飯）。"
        food_context = "熟悉香港茶餐廳、大牌檔、車仔麵等飲食文化。"
    else:
        persona = "台灣專業營養師，全程使用繁體中文，語氣親切自然（如：便當、滷肉飯、地瓜）。"
        food_context = "熟悉台灣夜市、手搖飲、便當店等飲食文化。"

    system_instruction = f"""
    你是一位專業的{persona}{food_context}你的諮詢對象是一名{gender}性。
    請遵循以下步驟：
    1. 追問細節：若食物描述太簡略，請友善追問細節。
    2. 提供分析：估算總卡路里、分析三大營養素比例、給予健康評分 (1-10分)。
    3. 健康建議：給出貼地的替代方案或健康食法。
    4. 營養標籤指令 (非常重要)：如果發現用戶飲食有明顯缺失，請在回覆的最尾段，單獨一行輸出對應的隱藏標籤（只能輸出標籤，不要解釋）：
       - 如果蛋白質嚴重不足 -> 輸出 [NEED_PROTEIN]
       - 如果蔬菜/纖維嚴重不足 -> 輸出 [NEED_FIBER]
       - 如果整體營養極度不均衡 -> 輸出 [NEED_VITAMIN]
       - 如果用戶想食邪惡零食 -> 輸出 [NEED_HEALTHY_SNACK]
    """

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "哈囉！今日食咗啲咩呀？" if region == "香港 (廣東話)" else "哈囉！今天吃了些什麼呢？"}]

    for msg in st.session_state.messages:
        if msg["role"] == "assistant":
            # 顯示時過濾掉 AI 給的隱藏標籤，保持介面乾淨
            clean_text = msg["content"].replace("[NEED_PROTEIN]", "").replace("[NEED_FIBER]", "").replace("[NEED_VITAMIN]", "").replace("[NEED_HEALTHY_SNACK]", "")
            with st.chat_message("assistant"):
                st.markdown(clean_text)
        else:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

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
                assistant_reply = response.text
                
                # 1. 顯示 AI 乾淨的回覆 (隱藏標籤)
                display_text = assistant_reply.replace("[NEED_PROTEIN]", "").replace("[NEED_FIBER]", "").replace("[NEED_VITAMIN]", "").replace("[NEED_HEALTHY_SNACK]", "")
                st.markdown(display_text)
                
                # 2. 觸發聯盟行銷推薦
                if "[NEED_PROTEIN]" in assistant_reply:
                    st.success(AFFILIATE_LINKS["PROTEIN"])
                if "[NEED_FIBER]" in assistant_reply:
                    st.success(AFFILIATE_LINKS["FIBER"])
                if "[NEED_VITAMIN]" in assistant_reply:
                    st.success(AFFILIATE_LINKS["VITAMIN"])
                if "[NEED_HEALTHY_SNACK]" in assistant_reply:
                    st.success(AFFILIATE_LINKS["HEALTHY_SNACK"])

                st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

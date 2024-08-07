import streamlit as st
from utils import parse_info

def agent_info():
    with st.expander("🤖 Agent信息填写"):
        st.write("**Agent信息查询**")
        st.write("**我的Agent - 发布 - API服务**")

        options = ["uat", "test", "lingda"]
        platform = st.radio(
            "**选择环境**",
            options,
            index=0,
            horizontal=True
        )

        allinfo = st.text_input("**快速输入**", placeholder="点击API服务的复制按钮", key="allinfo").strip()

        # 初始值
        uuid = ""
        authkey = ""
        authsecret = ""

        if allinfo:
            parsed_info = parse_info(allinfo)
            uuid = parsed_info.get("Uuid", "")
            authkey = parsed_info.get("AuthKey", "")
            authsecret = parsed_info.get("AuthSecret", "")

        # 这里使用解析后的值填充输入框，并给每个输入框设置唯一的 key
        uuid = st.text_input("**Uuid**:red[*]", value=uuid, placeholder="请输入uuid", key="uuid").strip()
        authkey = st.text_input("**AuthKey**:red[*]", value=authkey, placeholder="请输入AuthKey", key="authkey").strip()
        authsecret = st.text_input("**AuthSecret**:red[*]", value=authsecret, placeholder="请输入AuthSecret", key="authsecret").strip()

        return uuid, authkey, authsecret, platform
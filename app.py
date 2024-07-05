import streamlit as st
import pandas as pd
import openai
from agent_batch_test import evaluate_prompt  # Ensure this function is imported if it is in the agent_batch_test module


def main():
    # st.header("Agent Batch Test")
    st.set_page_config(layout="wide")
    st.title(":red[Agent批量测试]:sunglasses:")
    st.write("""目前仅支持单轮对话""")

    host = "https://uat.agentspro.cn"
    uuid = st.text_input("Uuid", placeholder="请输入uuid")
    authkey = st.text_input("AuthKey", placeholder="请输入AuthKey")
    authsecret = st.text_input("AuthSecret", placeholder="请输入AuthSecret")

    openai.api_key = "fe5f6afae5bfffb5c4fa148b061977a1.9Ep40DMGOnBb3FTo"
    openai.base_url = "https://open.bigmodel.cn/api/paas/v4/"

    upload_file = st.file_uploader("上传你的测试文件")

    if not (uuid and authkey and authsecret and upload_file):
        st.button('开始批量测试！', disabled=True)
        st.warning('请输入所有信息')
    else:
        if st.button('开始批量测试！'):
            df = pd.read_csv(upload_file)
            st.dataframe(df, width=1800, height=400)
            result_df = evaluate_prompt(df, host, uuid, authkey, authsecret)
            st.dataframe(result_df, width=1800, height=400)

            result_df.to_csv('result.csv', index=False)
            with open('result.csv', 'rb') as f:
                st.download_button('下载测试结果文件', f, file_name='result.csv')


if __name__ == '__main__':
    main()

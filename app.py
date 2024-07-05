import streamlit as st
import pandas as pd
import openai
from agent_batch_test import evaluate_prompt  # Ensure this function is imported if it is in the agent_batch_test module


def main():
    st.set_page_config(layout="wide")
    st.write("""
    # Agent批量测试
    目前仅支持单轮对话
    """)

    Uuid = st.text_input("Uuid", placeholder="请输入uuid")
    Authkey = st.text_input("AuthKey", placeholder="请输入AuthKey")
    AuthSecret = st.text_input("AuthSecret", placeholder="请输入AuthSecret")

    # Add a select box for model_name
    model_name = st.selectbox(
        'Select Model Name',
        ('glm-4', 'Model_B', 'Model_C'),
        placeholder="Select contact method..."
    )

    openai.api_key = "fe5f6afae5bfffb5c4fa148b061977a1.9Ep40DMGOnBb3FTo"
    openai.base_url = "https://open.bigmodel.cn/api/paas/v4/"

    upload_file = st.file_uploader("上传你的测试文件")

    if upload_file:
        df = pd.read_csv(upload_file)
        st.dataframe(df, width=1800, height=400)
        result_df = evaluate_prompt(df, model_name)
        st.write(result_df)
        # csv_path = '/mnt/data/result.csv'
        # result_df.to_csv(csv_path, index=False)
        # with open(csv_path, 'rb') as f:
        #     st.download_button('Download CSV', f, file_name='result.csv')


if __name__ == '__main__':
    main()

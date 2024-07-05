import streamlit as st
import pandas as pd
import openai
from agent_batch_test import evaluate_prompt


def main():
    # 固定变量
    host = "https://uat.agentspro.cn"
    openai.api_key = "fe5f6afae5bfffb5c4fa148b061977a1.9Ep40DMGOnBb3FTo"
    openai.base_url = "https://open.bigmodel.cn/api/paas/v4/"

    # 网页设置
    st.set_page_config(page_title="AgentAcc Batch Test", layout="wide", page_icon="page_icon.jpg")
    css = """
       <style>
       [data-testid="stSidebar"][aria-expanded="true"]{
           min-width: 450px;
           max-width: 450px;
       }
       """
    st.markdown(css, unsafe_allow_html=True)

    # 主页面
    st.title("Agent准确率批量测试:sunglasses:")
    st.write("""目前仅支持单轮对话""")

    # 侧边栏
    st.sidebar.write("**请先下载问答对模板，在本地制作好问答对**")
    df_template = pd.DataFrame(data={'提示词': ["（示例）中国的首都在哪里？"], '期望输出': ["北京"]})
    df_template.to_excel("template.xlsx", index=False)
    with open('template.xlsx', 'rb') as f:
        st.sidebar.download_button('问答对模板.xlsx', f, file_name='问答对模板.xlsx')
    st.sidebar.write("**以下内容位置：你的Agent - 右上角三个点 - 发布 - API Key**")
    uuid = st.sidebar.text_input("**Uuid**", placeholder="请输入uuid")
    authkey = st.sidebar.text_input("**AuthKey**", placeholder="请输入AuthKey")
    authsecret = st.sidebar.text_input("**AuthSecret**", placeholder="请输入AuthSecret")
    upload_file = st.sidebar.file_uploader("**上传你的测试文件(.csv或.xslx)，目前仅支持单文件**")

    # 处理用户无意输入的空格
    uuid = uuid.strip()
    authkey = authkey.strip()
    authsecret = authsecret.strip()

    # 确保输入信息完整，才可进行测试
    if not (uuid and authkey and authsecret and upload_file):
        st.button('开始批量测试！', disabled=True)
        st.warning('请在侧边栏输入所有信息')
    else:
        # 兼容csv和xlsx
        if upload_file.name.endswith('.csv'):
            df = pd.read_csv(upload_file)
        elif upload_file.name.endswith('.xlsx'):
            df = pd.read_excel(upload_file)
        st.dataframe(df, width=1800, height=400)
        # 开始批量测试
        if st.button('开始批量测试！'):
            result_df, acc = evaluate_prompt(df, host, uuid, authkey, authsecret)
            st.dataframe(result_df, width=1800, height=400)
            st.write(f"Agent回答准确率: {acc}")
            # 下载测试结果文件
            result_df.to_csv('result.csv', index=False)
            with open('result.csv', 'rb') as f:
                st.download_button('下载测试结果文件', f, file_name='result.csv')


if __name__ == '__main__':
    main()

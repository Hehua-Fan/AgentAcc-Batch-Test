import streamlit as st
import pandas as pd
import openai
from agent_batch_test import evaluate_prompt, qa_pair_generator
import plotly.graph_objects as go
from configs import ZHIPU_AI_API_KEY, OPEN_AI_API_KEY, OPEN_AI_BASE_URL, AUTOAGENTS_HOST_NAME

# 加载数据函数
def load_data(file):
    if file.name.endswith('.csv'):
        return pd.read_csv(file)
    elif file.name.endswith('.xlsx'):
        return pd.read_excel(file)
    else:
        st.error("不支持的文件格式。请上传 .csv 或 .xlsx 文件。")
        return None

def parse_info(info_str):
    info_dict = {}
    # 以空格分割
    segments = info_str.split()
    for segment in segments:
        # 以冒号分割键值对
        key, value = segment.split("：")
        info_dict[key.strip()] = value.strip()
    return info_dict

# 获取默认数据函数
def get_default_data():
    return pd.DataFrame({
        '提示词': ["（示例）中国的首都在哪里？"],
        '期望输出': ["北京"]
    })

def main():
    # 固定变量
    host = AUTOAGENTS_HOST_NAME
    openai.api_key = OPEN_AI_API_KEY
    openai.base_url = OPEN_AI_BASE_URL

    # 网页设置
    st.set_page_config(page_title="AgentAcc Batch Test", layout="wide", page_icon="🎯")
    
    css = """
       <style>
       [data-testid="stSidebar"][aria-expanded="true"]{
           min-width: 450px;
           max-width: 450px;
       }
       </style>
    """
    st.markdown(css, unsafe_allow_html=True)

    # 主页面标题
    st.title("Agent准确率批量测试 🚀")

    # 侧边栏
    with st.sidebar:
        # 问答对生成器
        with st.expander("💡 问答对生成器（选用工具）"):
            st.write("如果报错，很可能是由于敏感词问题")
            
            num_group = st.text_input("**问答对组数（选填）***", placeholder="默认：5组").strip()
            context = st.text_area("**背景信息（选填）***", placeholder="默认：无，例如：这个电话客服是基于线下实体店的，是线下类似于剧本杀，棋牌游戏的服务行业").strip()
            question = st.text_input("**期望问题（必填）**", placeholder="例如：客户的电话投诉").strip()
            answer = st.text_input("**期望回答（必填）**", placeholder="例如：标准而礼貌的客服回复").strip()
            
            start_qa_generator = st.button('🚀 开始生成问答对！', disabled=not all([question, answer]))
            
            if start_qa_generator:
                with st.spinner('正在进行生成...'):
                    # Provide default context if not supplied
                    default_num_group = "5" if not num_group else num_group
                    default_context = "这个电话客服是基于线下实体店的，是线下类似于剧本杀，棋牌游戏的服务行业" if not context else context
                    
                    qa_pair_df = qa_pair_generator(ZHIPU_AI_API_KEY, question, answer, default_num_group, default_context)
                    qa_pair_df.to_excel('生成的问答对.xlsx', index=False)
                
                with open('生成的问答对.xlsx', 'rb') as f_qa:
                    st.download_button('下载生成的问答对.xlsx', f_qa, file_name='生成的问答对.xlsx')

            else:
                st.warning('请描述想要生成的问答对')
            
        with st.expander("📥 下载测试模板"):
            st.write("可在本地编辑测试模版")
            default_df = get_default_data()
            default_df.to_excel('测试模板.xlsx', index=False)
            with open('测试模板.xlsx', 'rb') as f_template:
                st.download_button('下载测试结果文件.xlsx', f_template, file_name='测试模板.xlsx')

        with st.expander("🤖 Agent信息填写"):
            st.write("**Agent信息查询：**")
            st.write("**我的Agent - 发布 - API服务**")

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
            uuid = st.text_input("**Uuid***", value=uuid, placeholder="请输入uuid", key="uuid").strip()
            authkey = st.text_input("**AuthKey***", value=authkey, placeholder="请输入AuthKey", key="authkey").strip()
            authsecret = st.text_input("**AuthSecret***", value=authsecret, placeholder="请输入AuthSecret", key="authsecret").strip()
            
        upload_file = st.file_uploader("**上传你的测试模版(.csv或.xlsx)**")

    # 数据加载和显示
    if 'df' not in st.session_state:
        if upload_file is None:
            st.session_state.df = get_default_data()
        else:
            st.session_state.df = load_data(upload_file)
            if st.session_state.df is not None and 'Agent回答' not in st.session_state.df.columns:
                st.session_state.df['Agent回答'] = ''
            if st.session_state.df is not None and '是否正确' not in st.session_state.df.columns:
                st.session_state.df['是否正确'] = ''

    st.subheader("📊 测试数据")
    start_test = st.button('🚀 开始批量测试！', key='start_test_button', disabled=not all([uuid, authkey, authsecret]))

    create_aggrid(st.session_state.df)

    if not all([uuid, authkey, authsecret]):
        st.warning('⚠️ 请在侧边栏填写🤖Agent信息')
    elif start_test:
        with st.spinner('正在进行测试...'):
            result_df, acc = evaluate_prompt(st.session_state.df, host, uuid, authkey, authsecret)
        
        st.write("")
        st.subheader("🔍 测试结果")
        st.metric("Agent回答准确率：", f"{acc:.2%}")
        create_aggrid(result_df, editable=False)

        # 下载测试结果文件
        result_df.to_excel('测试结果.xlsx', index=False)
        with open('测试结果.xlsx', 'rb') as f_res:
            st.download_button('下载测试结果文件.xlsx', f_res, file_name='测试结果.xlsx')

if __name__ == '__main__':
    main()

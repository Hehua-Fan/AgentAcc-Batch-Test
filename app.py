import streamlit as st
import pandas as pd
import openai
from agent_batch_test import evaluate_prompt, qa_pair_generator
from st_aggrid import AgGrid, GridOptionsBuilder
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

# 创建AgGrid表格函数
def create_aggrid(df, editable=True):
    # gb = GridOptionsBuilder.from_dataframe(df)
    # gb.configure_default_column(editable=editable, filterable=True)
    # gridOptions = gb.build()
    # return AgGrid(
    #     df,
    #     gridOptions=gridOptions,
    #     data_return_mode='AS_INPUT',
    #     update_mode='MODEL_CHANGED',
    #     fit_columns_on_grid_load=True,
    #     theme='streamlit',
    #     height=400,
    #     width='100%'
    # )
    
    edited_df = st.data_editor(df, num_rows="dynamic")
    return edited_df

def main():
    # 固定变量
    host = AUTOAGENTS_HOST_NAME
    openai.api_key = OPEN_AI_API_KEY
    openai.base_url = OPEN_AI_BASE_URL

    # 网页设置
    st.set_page_config(page_title="AgentAcc Batch Test", layout="wide", page_icon="🎯")
    
    st.markdown("""
        <style>
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .stAlert {
            margin-top: 1rem;
        }
        .st-emotion-cache-1y4p8pa {
            max-width: 1000px;
        }
        </style>
        """, unsafe_allow_html=True)

    # 主页面标题
    st.title("Agent准确率批量测试 🚀")

    # 侧边栏
    with st.sidebar:
        with st.expander("💡 问答对生成器（选用工具）"):
            topic = st.text_area("**问答对主题***", placeholder="帮我生成一组问答对，问题是客户的电话投诉，回答是标准而礼貌的客服回复").strip()
            with st.spinner('正在进行生成...'):
                qa_pair_df = qa_pair_generator(topic, ZHIPU_AI_API_KEY)
                qa_pair_csv = qa_pair_df.to_csv(index=False)
            st.download_button('下载生成的问答对.csv', qa_pair_csv, file_name='生成的问答对.csv')

        with st.expander("📥 下载测试模板"):
            st.write("可在本地编辑测试模版")
            default_df = get_default_data()
            csv = default_df.to_csv(index=False)
            st.download_button('下载测试模板.csv', csv, file_name='测试模板.csv')

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
    if upload_file is None:
        df = get_default_data()
    else:
        df = load_data(upload_file)
        if df is not None and 'Agent回答' not in df.columns:
            df['Agent回答'] = ''
        if df is not None and '是否正确' not in df.columns:
            df['是否正确'] = ''

    st.subheader("📊 测试数据")
    start_test = st.button('🚀 开始批量测试！', key='start_test_button', disabled=not all([uuid, authkey, authsecret]))

    grid_response = create_aggrid(df)
    # df = grid_response['data']
    df = grid_response

    if not all([uuid, authkey, authsecret]):
        st.warning('⚠️ 请在侧边栏填写🤖Agent信息')
    elif start_test:
        with st.spinner('正在进行测试...'):
            result_df, acc = evaluate_prompt(df, host, uuid, authkey, authsecret)
        
        # 更新原有表格的数据
        df['Agent回答'] = result_df['Agent实际输出']
        df['是否正确'] = result_df['是否准确']

        st.write("") 
        st.subheader("🔍 测试结果")
        st.metric("Agent回答准确率：", f"{acc:.2%}")
        create_aggrid(df, editable=False)

        # 下载测试结果文件
        csv = df.to_csv(index=False)
        st.download_button('📥 下载测试结果文件', csv, file_name='测试结果.csv')


if __name__ == '__main__':
    main()
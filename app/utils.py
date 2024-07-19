import pandas as pd
import streamlit as st
import re


def load_data(file):
    if file.name.endswith('.csv'):
        return pd.read_csv(file)
    elif file.name.endswith('.xlsx'):
        return pd.read_excel(file)
    else:
        st.error("不支持的文件格式。请上传 .csv 或 .xlsx 文件。")
        return None
    
def download_file(label, file_name, df):
    df.to_excel(file_name,index=False)
    with open(file_name, 'rb') as f:
        st.download_button(label=label, data=f, file_name=file_name)


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

def get_default_data_without_expectation():
    return pd.DataFrame({
        '提示词': ["（示例）中国的首都在哪里？"],
    })

# 创建AgGrid表格函数
def create_aggrid(df, editable=True):
    edited_df = st.data_editor(df, num_rows="dynamic")
    return edited_df

def extract_json(text):
    if "```json" in text:
        pattern = re.compile(r'```json(.*?)\```', re.DOTALL)
        match = pattern.search(text.replace('\n',''))
        if match:
            return match.group(1)  # 返回匹配的JSON字符串
        else:
            return text  # 如果没有找到匹配的模式，则返回None
    else:
        return text
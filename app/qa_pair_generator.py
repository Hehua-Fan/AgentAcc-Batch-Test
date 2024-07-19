import streamlit as st
import pandas as pd
import json
from zhipuai import ZhipuAI
from configs import ZHIPU_AI_API_KEY, SYSTEM_PROMPT_QA_PAIR
from utils import download_file


def qa_pair_llm(ZHIPU_AI_API_KEY, question, answer, num_group, context):
    system_prompt = SYSTEM_PROMPT_QA_PAIR

    user_prompt = f"""
    我想生成的问答组数为{num_group},
    应用背景为{context},
    问题为{question},
    回答为{answer}
    """

    client = ZhipuAI(api_key=ZHIPU_AI_API_KEY)
    response = client.chat.completions.create(
        model="glm-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
    )

    response_str = response.choices[0].message.content

    if '`json' in response_str:
        response_str_extracted = response_str.split('`json')[1].split('`')[0].strip()
    else:
        response_str_extracted = response_str.strip()
    
    try:
        response_json = json.loads(response_str_extracted)
        df = pd.DataFrame.from_dict(response_json)
        return df
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)
        return None


def qa_pair_generator():
    with st.expander("💡 问答对生成器（选用工具）"):
        st.write("如果报错，很可能是由于敏感词问题")
        
        num_group = st.text_input("**问答对组数（选填）***", placeholder="默认：5组（最大组数为12）").strip()
        context = st.text_area("**背景信息（选填）***", placeholder="默认：无，例如：这个电话客服是基于线下实体店的，是线下类似于剧本杀，棋牌游戏的服务行业").strip()
        question = st.text_input("**期望问题（必填）**", placeholder="例如：客户的电话投诉").strip()
        answer = st.text_input("**期望回答（必填）**", placeholder="例如：标准而礼貌的客服回复").strip()
        
        start_qa_generator = st.button('🚀 开始生成问答对！', disabled=not all([question, answer]))
        
        if start_qa_generator:
            with st.spinner('正在进行生成...'):
                # Provide default context if not supplied
                default_num_group = "5" if not num_group else num_group
                if int(default_num_group) > 12:
                    default_num_group = "12"
                elif int(default_num_group) < 1:
                    default_num_group = "1"
                default_context = "这个电话客服是基于线下实体店的，是线下类似于剧本杀，棋牌游戏的服务行业" if not context else context
                
                qa_pair_df = qa_pair_llm(ZHIPU_AI_API_KEY, question, answer, default_num_group, default_context)
            
            # 下载按钮
            download_file("下载生成的问答对.xlsx", "生成的问答对.xlsx", qa_pair_df)

        else:
            st.warning('请描述想要生成的问答对')
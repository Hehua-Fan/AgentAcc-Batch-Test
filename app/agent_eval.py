import openai
import json
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from configs import SYSTEM_PROMPT_EVAL, AUTOAGENTS_HOST_NAME_UAT, AUTOAGENTS_HOST_NAME_TEST, AUTOAGENTS_HOST_NAME_LINGDA, ZHIPU_AI_API_KEY, MODEL_BASE_URL
from utils import extract_json
import streamlit as st
from stqdm import stqdm

def eval_model(prompt, actual_output, expected_output):
    system_prompt = SYSTEM_PROMPT_EVAL

    user_prompt =f"""
我想让你模拟文本内容一致性分析师,你最终的输出为一个JSON字符串。

# Role：文本内容一致性分析师

## Background：
在自然语言处理领域，文本内容的对比分析是一个常见的任务，用于判断两个文本是否表达相同的信息。

## Goals:
- 请结合用户的问题，分析给定的两段文本，确定它们是否在内容上相符。
- 输出一个结构化的json格式结果，明确表示文本一致性判定。

## Constrains:
- 必须仅仅基于提供的文本内容来做出判断，不得引入外部信息。
- 输出结果必须是json格式，确保数据的可用性和一致性。

## Workflow:
1. 接收并读取两段文本输入,<文本1> </文本1>和<文本2> </文本2>。
2. 应用文本相似度对比两段文本。
3. 根据结果判定两文本是否内容相符。
4. 封装判定结果到json格式，输出json。

## 以下是文本1和文本2信息：
<文本1>{actual_output}</文本1>
<文本2>{expected_output}</文本2>

以json格式输出最终结果。
正确输出示例：{{ "result": true }} 或 {{ "result": false }}
"""
    
    response = openai.chat.completions.create(
        model="glm-4-airx",
        messages=[
            {"role": "system", "content": "你是AI助手,专门输出JSON格式数据。"},
            {"role": "user", "content": user_prompt}
        ],
        top_p=0.7,
        temperature=0.9,
        response_format={"type": "json_object"}
    )
    message = response.choices[0].message.content

    json_str = extract_json(message)
    try:
        boolean = json.loads(json_str)['result']
    except Exception as e:
        print(f"模型没有正确输出json格式，模型输出：{json_str}")
        return False
    return boolean

def agent_api(prompt, uuid, authKey, authSecret, platform):
    # 环境变量
    if platform == 'uat':
        host = AUTOAGENTS_HOST_NAME_UAT
    elif platform == 'test':
        host = AUTOAGENTS_HOST_NAME_TEST
    else:
        host = AUTOAGENTS_HOST_NAME_LINGDA
    openai.api_key = ZHIPU_AI_API_KEY
    openai.base_url = MODEL_BASE_URL
    url = host + "/openapi/agent/chat/completions/v1"
    headers = {
        "Authorization": f"Bearer {authKey}.{authSecret}"
    }
    body = {
        "agentId": f"{uuid}",
        "chatId": None,
        "userChatInput": f"{prompt}"
    }

    # 发送POST请求
    response = requests.post(url, headers=headers, json=body)

    # 检查响应状态码
    if response.status_code == 200:
        try:
            # 尝试将响应解析为JSON
            json_response = response.json()
            # 检查 "choices" 列表是否存在且不为空
            if "choices" in json_response and len(json_response["choices"]) > 0:
                conten = json_response["choices"][0]["content"]
                #print(conten)
                return conten
            else:
                print("The 'choices' list is empty or not present in the response.",json_response)
                return ""
        except ValueError:
            # 如果响应不是JSON格式，打印原始文本
            print("Response content is not in JSON format:", response.text)
            return ""
    else:
        print(f"Request failed with status code {response.status_code}")
        return ""

def agent_eval(df, uuid, authkey, authsecret, IsEvaluate, placeholder, platform, num_threads):
    num_correct, num_total = 0, df.shape[0]
    actual_output = [""] * num_total
    judgement = [None] * num_total if IsEvaluate else None
    
    lock = Lock()

    def process_row(i):
        prompt = df.iloc[i, 0]
        response = agent_api(prompt, uuid, authkey, authsecret, platform)
        
        if IsEvaluate:
            tf = eval_model(prompt, response, df.iloc[i, 1])
            return i, response, tf
        else:
            return i, response, None

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_to_index = {executor.submit(process_row, i): i for i in range(num_total)}
        completed = 0

        for future in stqdm(as_completed(future_to_index), total=num_total, desc="当前测试进度"):
            i, response, tf = future.result()
            with lock:
                actual_output[i] = response
                if IsEvaluate:
                    judgement[i] = tf
                    if tf :
                        num_correct += 1
                
                completed += 1
                
                if completed % 1 == 0 or completed == num_total:  # 每次更新，或在最后更新
                    if IsEvaluate:
                        temp_df = pd.DataFrame({
                            '问题': df.iloc[:, 0],
                            '期望输出': df.iloc[:, 1],
                            'Agent回答': actual_output,
                            '是否正确': judgement
                        })
                    else:
                        temp_df = pd.DataFrame({
                            '问题': df.iloc[:, 0],
                            'Agent回答': actual_output
                        })
                    
                    placeholder.dataframe(temp_df)
                    st.session_state.last_df = temp_df  # 保存最后的DataFrame

    final_df = st.session_state.last_df
    accuracy = num_correct / num_total if IsEvaluate else "Not Important"

    return final_df, accuracy
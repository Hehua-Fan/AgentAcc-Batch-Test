import openai
import json
import requests
import pandas as pd
from stqdm import stqdm
from configs import SYSTEM_PROMPT_EVAL, AUTOAGENTS_HOST_NAME, ZHIPU_AI_API_KEY, MODEL_BASE_URL
from utils import extract_json

def eval_model(prompt, actual_output, expected_output):
    system_prompt = SYSTEM_PROMPT_EVAL

    user_prompt = f"""
    <背景信息>{prompt}</背景信息>
    <文本1>{actual_output}</文本1>
    <文本2>{expected_output}</文本2>
    """
    response = openai.chat.completions.create(
        model="glm-4",
        messages=[
            {"role": "system", "content": system_prompt},
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

def agent_api(prompt, uuid, authKey, authSecret):
    # 环境变量
    host = AUTOAGENTS_HOST_NAME
    openai.api_key = ZHIPU_AI_API_KEY
    openai.base_url = MODEL_BASE_URL
    url = host + "/openapi/agent/chat/completions/v1"
    headers = {
        "Authorization": f"Bearer {authKey}.{authSecret}"
    }
    body = {
        "agentId": f"{uuid}",
        "chatId": None,
        "userChatInput": f"{prompt}",
    }

    # 发送POST请求
    response = requests.post(url, headers=headers, json=body)

    # 检查响应状态码
    if response.status_code == 200:
        try:
            # 尝试将响应解析为JSON
            json_response = response.json()
            return json_response["choices"][0]["content"]
        except ValueError:
            # 如果响应不是JSON格式，打印原始文本
            print("Response content is not in JSON format:", response.text)
    else:
        print(f"Request failed with status code {response.status_code}")

def agent_eval(df, uuid, authkey, authsecret, IsEvaluate, placeholder):
    num_correct, num_total = 0, df.shape[0]
    actual_output, judgement = [], []

    for i in stqdm(range(df.shape[0]), desc="当前测试进度"):
        prompt = df.iloc[i, 0]
        response = agent_api(prompt, uuid, authkey, authsecret)
        actual_output.append(response)
        if IsEvaluate:
            tf = eval_model(prompt, response, df.iloc[i, 1])
            judgement.append(tf)
            if tf == "True":
                num_correct += 1

        # 实时更新DataFrame
        if IsEvaluate:
            temp_df = pd.DataFrame(data={'问题': df.iloc[:i+1, 0],
                                         '期望输出': df.iloc[:i+1, 1],
                                         'Agent回答': actual_output,
                                         '是否正确': judgement})
        else:
            temp_df = pd.DataFrame(data={'问题': df.iloc[:i+1, 0],
                                         'Agent回答': actual_output})
        placeholder.write(temp_df)

    if IsEvaluate:
        df = pd.DataFrame(data={'问题': df.iloc[:, 0],
                                '期望输出': df.iloc[:, 1],
                                'Agent回答': actual_output,
                                '是否正确': judgement})
        accuracy = num_correct / num_total
    else:
        df = pd.DataFrame(data={'问题': df.iloc[:, 0],
                                'Agent回答': actual_output})
        accuracy = "Not Important"

    return df, accuracy

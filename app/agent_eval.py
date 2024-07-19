import openai
import json
import requests
import pandas as pd
from stqdm import stqdm
from configs import SYSTEM_PROMPT_EVAL
from utils import extract_json


def eval_model(prompt, actual_output, expected_output):
    system_prompt = SYSTEM_PROMPT_EVAL

    user_prompt = f"""
    <背景信息>{prompt}</背景信息>
    <文本1>{actual_output}</文本1>
    <文本2>{expected_output}</文本2>
    """
    response = openai.chat.completions.create(
        model = "glm-4",
        messages=[
            {"role":"system", "content":system_prompt},
            {"role":"user", "content":user_prompt}
        ],
        top_p=0.7,
        temperature=0.9,
        response_format= { "type": "json_object" }
    )
    meassage = response.choices[0].message.content

    json_str = extract_json(meassage)
    try:
        boolean = json.loads(json_str)['result']
    except Exception as e:
        print(f"模型没有正确输出json格式，模型输出：{json_str}")
        return False
    return boolean

def agent_api(prompt, host, uuid, authKey, authSecret):
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
            # Try to parse the response as JSON
            json_response = response.json()
            return json_response["choices"][0]["content"]
        except ValueError:
            # If the response is not JSON, print the raw text
            print("Response content is not in JSON format:", response.text)
    else:
        print(f"Request failed with status code {response.status_code}")

def agent_eval(df, host, uuid, authkey, authsecret, IsEvaluate):
    num_correct, num_total = 0, df.shape[0]
    actual_output, judgement = [], []

    for i in stqdm(range(df.shape[0]), desc="当前测试进度"):
        prompt = df.iloc[i,0]
        response = agent_api(prompt, host, uuid, authkey, authsecret)
        actual_output.append(response)
        if IsEvaluate:
            tf = eval_model(prompt, response, df.iloc[i,1])
            judgement.append(tf)
            if tf == "True":
                num_correct += 1

    if IsEvaluate:
        df = pd.DataFrame(data={'提示词': df.iloc[:,0],
                           '期望输出': df.iloc[:,1],
                           'Agent实际输出': actual_output,
                           '是否准确': judgement})
        accuracy = num_correct / num_total
    else:
        df = pd.DataFrame(data={'提示词': df.iloc[:,0],
                           'Agent实际输出': actual_output})
        accuracy = "Not Important"

    return df, accuracy
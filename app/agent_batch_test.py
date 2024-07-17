import openai
import json
import re 
import requests
import pandas as pd
from stqdm import stqdm
from zhipuai import ZhipuAI
from configs import ZHIPU_AI_API_KEY
import streamlit as st

def qa_pair_generator(ZHIPU_AI_API_KEY, question, answer, num_group, context):
    system_prompt = """
    # Role：请根据我的主题和问题，帮我生成我想要的问答对
    # Format
    请以json格式输出，以Question, Answer作为Key，以下是示例，只是在向你展示格式：
    {
        "Question": [
            "为什么我的服务这么慢？",
            "我什么时候能收到我订购的商品？"
        ],
        "Answer": [
            "很抱歉给您带来了不便，我们会立即为您查看原因并尽快解决，请您提供一下相关信息以便我们更好地帮助您。",
            "感谢您的耐心等待，根据我们的系统显示，您的商品将在接下来的3-5天内送达。如果有任何问题，我们会及时与您联系。"
        ]
    }   
    """

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
    response_str_extracted = response_str.split('`json')[1].split('`')[0].strip()
    response_json = json.loads(response_str_extracted)
    df = pd.DataFrame.from_dict(response_json)
    
    return df

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

def evaluate_model(prompt, actual_output, expected_output):
    system_prompt = """
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
    4. 封装判定结果到json格式，输出。
    

    ## strict output format:
    - 只输出最终结果，以json格式输出。
    - 例如：{ "result": "True" } 或 { "result": "False" }
    """

    user_prompt = f"""
    用户的问题：{prompt}
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

def api_model(prompt, host, uuid, authKey, authSecret):
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

def evaluate_prompt(df, host, uuid, authkey, authsecret):
    num_correct, num_total = 0, df.shape[0]
    actual_output, judgement = [], []

    for i in stqdm(range(df.shape[0]), desc="当前测试进度"):
        prompt = df.iloc[i, 0]
        response = api_model(prompt, host, uuid, authkey, authsecret)
        tf = evaluate_model(prompt, response, df.iloc[i, 1])
        actual_output.append(response)
        judgement.append(tf)
        if tf == "True":
            num_correct += 1

        # Update DataFrame with current results
        df.at[i, 'Agent回答'] = response
        df.at[i, '是否正确'] = tf

        # Show updated results in Streamlit
        st.write(df)

    accuracy = num_correct / num_total

    return df, accuracy




if __name__ == "__main__":

    # 使用你的API密钥和基础URL初始化OpenAI客户端
    openai.api_key = "fe5f6afae5bfffb5c4fa148b061977a1.9Ep40DMGOnBb3FTo"
    openai.base_url = "https://open.bigmodel.cn/api/paas/v4/"
    host = "https://uat.agentspro.cn"

    # 智能党建助手
    Uuid = "49fc7957298f46c79a68738736d3680c"
    AuthKey = "49fc7957298f46c79a68738736d3680c"
    AuthSecret = "TQHqrhBv49NZf2n0B2aWJ7MqNzMYL7RE"

    df = pd.read_csv('问答对.csv')
    evaluate_prompt(df, host, Uuid, AuthKey, AuthSecret)
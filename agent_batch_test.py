import openai
import json
import re 
import requests
import pandas as pd
pd.set_option('display.max_rows', None)
from tqdm import tqdm

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

def evaluate_model(actual_output, expected_output, model_name):
    system_prompt = """
    # Role：文本内容一致性分析师

    ## Background：
    在自然语言处理领域，文本内容的对比分析是一个常见的任务，用于判断两个文本是否表达相同的信息。

    ## Attention：
    成功的文本匹配不仅需要对比直接的文字相似性，还要能够识别语义的一致性，即便面对语法或表达形式的差异。这是一项挑战但同时也非常关键的任务。

    ## Profile：
    - Language: 中文
    [描述]: 作为一个文本内容一致性分析师，专门帮助解决文本相似度判别问题，使用自然语言处理技术评估两段文本在语义上的相关性。

    ### Skills:
    - 丰富的自然语言处理知识，包括但不限于文本挖掘、语义分析和机器学习。
    - 能够处理和分析大量的文本数据，并从中提取有用信息。
    - 熟练操作多种文本相似度测试方法，包括余弦相似性、Jaccard相似性等。

    ## Goals:
    - 分析给定的两段文本，确定它们是否在内容上相符。
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
    <文本1>{actual_output}</文本1>
    <文本2>{expected_output}</文本2>
    """
    response = openai.chat.completions.create(
        model = model_name,
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

def chat_model(prompt, model):
    response = openai.chat.completions.create(
        model= model,
        messages=[
            {"role":"system", "content":"i am llm model"},
            {"role":"user", "content": prompt}
        ],
        top_p=0.7,
        temperature=0.9
    )
    return response.choices[0].message.content

def api_model(host, uuid, authKey, authSecret, prompt):
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
            print("LLM Response:", json_response["choices"][0]["content"])
        except ValueError:
            # If the response is not JSON, print the raw text
            print("Response content is not in JSON format:", response.text)
    else:
        print(f"Request failed with status code {response.status_code}")

def evaluate_prompt(df, model_name):
    correct = 0
    actual_output, judgement = [], []
    print(df)

    for i in tqdm(range(df.shape[0])):
        response = chat_model(df["prompt"][i], model_name)
        TF = evaluate_model(response, df["expected_output"][i],model_name)
        actual_output.append(response)
        judgement.append(TF)
        if judgement:
            correct += 1

    df = pd.DataFrame(data={'提示词': df["prompt"],
                       '期望输出': df["expected_output"],
                       '实际输出': actual_output,
                       '是否准确': judgement})

    df.to_csv("evaluation.csv", index=False)

    return df


    # accuracy = correct / total
    # print(f"准确率: {accuracy * 100:.2f}%")

if __name__ == "__main__":

    # 使用你的API密钥和基础URL初始化OpenAI客户端
    openai.api_key = "fe5f6afae5bfffb5c4fa148b061977a1.9Ep40DMGOnBb3FTo"
    openai.base_url = "https://open.bigmodel.cn/api/paas/v4/"
    model_name = "glm-4"
    host = "https://uat.agentspro.cn"

    # 智能党建助手
    uuid = "49fc7957298f46c79a68738736d3680c"
    auth_key = "49fc7957298f46c79a68738736d3680c"
    auth_secret = "TQHqrhBv49NZf2n0B2aWJ7MqNzMYL7RE"

    prompts = pd.read_csv('prompts.csv')
    evaluate_prompt(prompts, model_name)
    api_model(host, uuid, auth_key, auth_secret, prompt="1")
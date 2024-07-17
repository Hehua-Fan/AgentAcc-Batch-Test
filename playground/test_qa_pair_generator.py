import pandas as pd
from zhipuai import ZhipuAI
import json

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


if __name__ == '__main__':
    ZHIPU_AI_API_KEY = ""
    num_group = 5
    context = "这个电话客服是基于线下实体店的，是线下类似于剧本杀，棋牌游戏的服务行业"
    question = "客户的电话投诉"
    answer = "标准而礼貌的客服回复"
    df = qa_pair_generator(ZHIPU_AI_API_KEY, question, answer, num_group, context)
    df.to_csv('qa_pairs.csv', index=False, encoding='utf-8-sig')
    print(df)
import pandas as pd
from zhipuai import ZhipuAI
import json

def qa_pair_generator(ZHIPU_AI_API_KEY, question, answer, num_group=5, context=""):
    system_prompt = """
    # Role：请根据我的主题和问题，帮我生成我想要的问答对
    # Format
    请以json格式输出，以Question, Answer作为Key，直接书写问题和回答，不需要冒号，例如：
    {
        "Question": [
            "问题1",
            "问题2"
        ],
        "Answer": [
            "回答1",
            "回答2"
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
    response_json = json.loads(response_str)
    
    df = pd.DataFrame(response_json)
    
    return df

if __name__ == '__main__':
    topic = "帮我生成一组问答对，问题是客户的电话投诉，回答是标准而礼貌的客服回复"
    df=qa_pair_generator(topic)
    print(df)
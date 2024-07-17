# AgentAcc-Batch-Test
![alt text](src/img.png)

## Quick Start
There is a website can be used directly to demo.
>https://agentacc-batch-test.streamlit.app/

## Get Started
To get started with Local Multimodal AI Chat, clone the repository and follow these simple steps:

0. **Change your path at first, which the folder is located in**
```Shell
cd AgentAcc-batch-test
```

1. **Create a Virtual Environment**: I am using Python 3.9.16 currently
```shell
conda create -n <your_environment_name> python==3.9.16 -y
conda activate <your_environment_name>
```

2. **Install Requirements**
```shell
pip install -r requirements.txt
```

3. **Enter commands in terminal**
```shell
streamlit run app.py
```

## Possible Improvements
* 输入个人的API_KEY
* 限制问答对生成组数，限制批量测试数量
* 点击其他按钮或空白处会重新刷新页面，导致数据丢失
* 流式输出测试结果
* support multi-round dialogue

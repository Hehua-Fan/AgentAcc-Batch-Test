import pandas as pd

# 读取 Excel 文件
df = pd.read_excel('D:/公司文件/autoagensai/网络类/网络类数据.xlsx')

# 每300行切分数据
chunk_size = 100
for i in range(0, len(df), chunk_size):
    # 获取当前的300行数据
    chunk = df.iloc[i:i + chunk_size]
    
    # 将当前的300行数据保存到txt文件
    file_name = f'D:/公司文件/autoagensai/网络类/output_{i//chunk_size + 1}.txt'
    
    # 保存为txt文件，只保存第一列，不加索引和空行
    with open(file_name, 'w', newline='', encoding='utf-8') as f:
        f.write('\n'.join(chunk.iloc[:, 0].dropna().astype(str).tolist()))
    
    print(f'{file_name} saved.')

print("完成切分")

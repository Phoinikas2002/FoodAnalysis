# 分析评论最多人均消费最低商家

import pandas as pd

def load_data(file_path, encoding='utf-8'):
    """
    加载CSV文件并处理列名，返回DataFrame。
    """
    data = pd.read_csv(file_path, encoding=encoding)
    # 处理列名，去除空格等
    data.columns = data.columns.str.strip()
    # 对评论列进行处理
    data['评论'] = data['评论'].str.replace(r'(\d+)\s*条评价', r'\1', regex=True)
    # 转换评论列为数值类型
    data['评论'] = pd.to_numeric(data['评论'], errors='coerce')  # errors='coerce'用于处理非数值的情况
    # 转换人均消费列为数值类型
    data['人均消费'] = data['人均消费'].str.replace(r'人均: (\d+) 元', r'\1', regex=True)
    data['人均消费'] = pd.to_numeric(data['人均消费'], errors='coerce')
    return data

def assign_score(df, column, ascending=True):
    """
    对每个商家在指定列上的值进行排名，并根据分位数赋予相应的分数（10个等级）。
    """
    df[f'{column}_rank'] = df[column].rank(ascending=ascending, method='min')
    df[f'{column}_score'] = 0

    # 计算分位数
    quantiles = [df[f'{column}_rank'].quantile(i/10) for i in range(1, 10)]

    # 分配分数
    df.loc[df[f'{column}_rank'] <= quantiles[0], f'{column}_score'] = 10
    for i in range(1, 9):
        df.loc[(df[f'{column}_rank'] > quantiles[i-1]) & (df[f'{column}_rank'] <= quantiles[i]), f'{column}_score'] = 10 - i
    df.loc[df[f'{column}_rank'] > quantiles[8], f'{column}_score'] = 1

    return df

def calculate_total_score(df):
    """
    计算每个商家的总分数，按照指定权重。
    """
    # 定义权重
    weights = {'评论_score': 0.7, '人均消费_score': 0.3}

    # 计算总分数
    df['总分数'] = df['评论_score'] * weights['评论_score'] \
                + df['人均消费_score'] * weights['人均消费_score']

    return df

def main():
    # 加载CSV文件
    file_path = 'D:/Git/Nice-Food-Analysis/reptile/fooddata.csv'
    data = load_data(file_path, encoding='utf-8')

    # 处理评论和人均消费并计算分数
    data = assign_score(data, '评论', ascending=False)  # 评论越多分数越高
    data = assign_score(data, '人均消费', ascending=True)  # 人均消费越低分数越高

    # 计算总分数
    data = calculate_total_score(data)

    # 保留所需列
    result_columns = ['店名', '评论', '人均消费', '总分数']
    result = data[result_columns]

    # 根据总分数降序排序
    result = result.sort_values(by='总分数', ascending=False)

    # 输出结果
    output_file = 'D:/Git/Nice-Food-Analysis/analysis/highly_discussed_and_low_consumption.csv'
    result.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"结果已保存到文件: {output_file}")

if __name__ == "__main__":
    main()

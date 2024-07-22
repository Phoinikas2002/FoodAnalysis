# 分析环境评分最高，服务评分最高的商家

import pandas as pd

def load_data(file_path, encoding='utf-8'):
    """
    加载CSV文件并处理列名，返回DataFrame。
    """
    data = pd.read_csv(file_path, encoding=encoding)
    # 处理列名，去除空格等
    data.columns = data.columns.str.strip()
    # 转换环境评分和服务评分为数值类型
    data['环境'] = pd.to_numeric(data['环境'], errors='coerce')
    data['服务'] = pd.to_numeric(data['服务'], errors='coerce')
    return data

def find_top_scorers(df, column):
    """
    根据指定列的评分找到评分最高的所有商家。
    """
    max_score = df[column].max()
    top_scorers = df[df[column] == max_score]
    return top_scorers

def main():
    # 加载CSV文件
    file_path = 'D:/Git/Nice-Food-Analysis/reptile/fooddata.csv'
    data = load_data(file_path, encoding='utf-8')

    # 找到环境评分最高的商家（包括所有同分的）
    best_environment = find_top_scorers(data, '环境')

    # 找到服务评分最高的商家（包括所有同分的）
    best_service = find_top_scorers(data, '服务')

    # 输出结果
    print("环境评分最高的商家（包括同分的）:")
    print(best_environment[['店名', '环境']])
    print("\n服务评分最高的商家（包括同分的）:")
    print(best_service[['店名', '服务']])

    # 可选：保存结果到CSV文件
    output_file_env = 'D:/Git/Nice-Food-Analysis/analysis/best_environment.csv'
    output_file_service = 'D:/Git/Nice-Food-Analysis/analysis/best_service.csv'
    best_environment[['店名', '环境']].to_csv(output_file_env, index=False, encoding='utf-8-sig')
    best_service[['店名', '服务']].to_csv(output_file_service, index=False, encoding='utf-8-sig')

    print(f"\n结果已保存到文件: {output_file_env} 和 {output_file_service}")

if __name__ == "__main__":
    main()

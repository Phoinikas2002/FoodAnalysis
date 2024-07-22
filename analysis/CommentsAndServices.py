# 分析评论最多，服务评分最差的三个商家

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
    data['评论'] = pd.to_numeric(data['评论'], errors='coerce')
    # 转换服务评分为数值类型
    data['服务'] = pd.to_numeric(data['服务'], errors='coerce')
    return data


def analyze_top_comments_lowest_service(df, top_n=3):
    """
    分析评论最多且服务评分最差的商家。
    """
    # 找到评论最多的商家
    top_comments = df.sort_values(by='评论', ascending=False)

    # 取出评论最多的商家
    top_comments = top_comments.head(10)  # 取评论最多的前10个商家

    # 在这些商家中找到服务评分最低的商家
    lowest_service = top_comments.sort_values(by='服务').head(top_n)

    return lowest_service


def main():
    # 加载CSV文件
    file_path = 'D:/Git/Nice-Food-Analysis/reptile/fooddata.csv'
    data = load_data(file_path, encoding='utf-8')

    # 找到评论最多且服务评分最差的商家
    result = analyze_top_comments_lowest_service(data)

    # 输出结果
    print("评论最多且服务评分最差的三个商家:")
    print(result[['店名', '评论', '服务']])

    # 可选：保存结果到CSV文件
    output_file = 'D:/Git/Nice-Food-Analysis/analysis/top_comments_lowest_service.csv'
    result[['店名', '评论', '服务']].to_csv(output_file, index=False, encoding='utf-8-sig')

    print(f"\n结果已保存到文件: {output_file}")


if __name__ == "__main__":
    main()

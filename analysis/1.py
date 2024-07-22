import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Bar, Pie

# 将 CSV 数据读入 DataFrame
df = pd.read_csv('analysis\highly_discussed_and_low_consumption.csv', encoding='utf-8')
def create_horizontal_bar_chart(df):
    bar = (
        Bar()
        .add_xaxis(df['总分数'].tolist())  # X 轴为总分数
        .add_yaxis('总分数', df['总分数'].tolist(), label_opts=opts.LabelOpts(is_show=False))  # Y 轴为店名
        .set_global_opts(
            title_opts=opts.TitleOpts(title="餐馆总分数水平柱状图"),
            xaxis_opts=opts.AxisOpts(name="总分数", type_="value"),
            yaxis_opts=opts.AxisOpts(name="店名", type_="category", is_inverse=True),  # Y 轴设置为类别轴并反向显示
            datazoom_opts=opts.DataZoomOpts(type_='inside', orient='vertical')  # 设置垂直滚动条
        )
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    )
    return bar

# 生成图表
horizontal_bar_chart = create_horizontal_bar_chart(df)

# 渲染图表到本地文件
horizontal_bar_chart.render("horizontal_bar_chart.html")

# 创建包含滚动条的 HTML 文件
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>餐馆评分水平柱状图</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            padding: 0;
            background-color: #f4f4f4;
        }
        .container {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            overflow: hidden;
        }
        .chart-container {
            width: 100%;
            height: 600px;
            overflow-y: auto;  /* 添加垂直滚动条 */
            overflow-x: hidden;
            position: relative;
            border: 1px solid #ddd;
            background-color: #fff;
        }
        iframe {
            width: 100%;
            height: 100%;
            border: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="chart-container">
            <iframe src="horizontal_bar_chart.html" title="Horizontal Bar Chart"></iframe>
        </div>
    </div>
</body>
</html>
"""

# 保存包含滚动条的 HTML 文件
with open("charts_with_scroll.html", "w", encoding="utf-8") as file:
    file.write(html_content)

print("包含滚动条的 HTML 文件已生成：charts_with_scroll.html")
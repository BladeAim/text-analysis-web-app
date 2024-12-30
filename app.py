import streamlit as st
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from pyecharts.charts import WordCloud
from pyecharts import options as opts
import jieba
import requests
from bs4 import BeautifulSoup


# 抓取网页文本内容的函数
def get_text_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text()
    except requests.RequestException as e:
        st.error(f"获取网页内容出错: {e}")
        return ""


# 对文本进行分词并统计词频的函数，只统计两个字及以上且是字母数字组成的词汇（忽略单独数字）
def word_frequency(text):
    words = jieba.lcut(text)
    word_dict = {}
    for word in words:
        if len(word) >= 2 and word.isalnum():  # 只统计长度大于等于2且是字母数字组成的词汇
            if not (word.isdigit()):  # 排除单独的数字情况
                word_dict[word] = word_dict.get(word, 0) + 1
    return word_dict


# 绘制词云图的函数（原代码中的pyecharts绘制词云图部分保持不变）
def draw_word_cloud(word_dict):
    word_cloud = WordCloud()
    data = [(word, count) for word, count in word_dict.items()]
    word_cloud.add("", data, word_size_range=[20, 100])
    return word_cloud


# 使用Plotly绘制词频排名前20词汇柱状图的函数
def draw_bar_chart(word_dict):
    sorted_word_dict = sorted(word_dict.items(), key=lambda x: x[1], reverse=True)[:20]
    words = [item[0] for item in sorted_word_dict]
    counts = [item[1] for item in sorted_word_dict]
    fig = go.Figure(go.Bar(x=words, y=counts))
    fig.update_layout(title_text="词频排名前20的词汇")
    return fig


# 使用Plotly绘制折线图的函数
def draw_line_chart(word_dict):
    sorted_word_dict = sorted(word_dict.items(), key=lambda x: x[1], reverse=True)
    words = [item[0] for item in sorted_word_dict]
    counts = [item[1] for item in sorted_word_dict]
    fig = go.Figure(go.Scatter(x=words, y=counts, mode='lines'))
    fig.update_layout(title_text="词频变化折线图")
    return fig


# 使用Plotly绘制饼图的函数
def draw_pie_chart(word_dict):
    data = [(word, count) for word, count in word_dict.items()]
    fig = go.Figure(data=[go.Pie(labels=[d[0] for d in data], values=[d[1] for d in data])])
    fig.update_layout(title_text="词频占比饼图")
    return fig


# 使用Matplotlib绘制箱线图的函数
def draw_boxplot_chart(word_dict):
    counts = list(word_dict.values())
    plt.boxplot([counts])
    plt.title("词频箱线图")
    fig = plt.gcf()
    plt.close(fig)
    return fig


# 使用Plotly绘制散点图的函数，添加显示词汇名称的功能（鼠标悬停显示）
def draw_scatter_chart(word_dict):
    data = []
    for index, (word, count) in enumerate(word_dict.items()):
        data.append({"name": word, "value": [index, count]})

    x_values = [d["value"][0] for d in data]
    y_values = [d["value"][1] for d in data]
    hover_text = [d["name"] for d in data]

    fig = go.Figure(data=go.Scatter(x=x_values, y=y_values, mode='markers', text=hover_text, hoverinfo='text+x+y'))
    fig.update_layout(title_text="词频散点图")
    return fig


# 使用Plotly绘制雷达图的函数，修改此处使数据呈圆形分布
def draw_radar_chart(word_dict):
    categories = ['词频']
    data = []
    for word, count in word_dict.items():
        data.append(go.Scatterpolar(r=[count], theta=[categories[0]], fill='toself', name=word))

    fig = go.Figure(data=data)
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True)),
        title_text="词频雷达图"
    )
    return fig


# 主函数
def main():
    st.title("文本词频分析与可视化")
    url = st.text_input("请输入文章URL:")
    if url:
        text = get_text_from_url(url)
        word_dict = word_frequency(text)
        st.sidebar.title("图形筛选")
        # 提供7种图形选项供用户选择
        graph_type = st.sidebar.selectbox("选择图形类型", ["词云图", "词频前20柱状图", "折线图", "饼图", "箱线图", "散点图", "雷达图"])
        filter_threshold = st.sidebar.slider("过滤低频词阈值", min_value=0, max_value=max(word_dict.values()), value=0, step=1)
        filtered_word_dict = {word: count for word, count in word_dict.items() if count >= filter_threshold}

        if graph_type == "词云图":
            word_cloud = draw_word_cloud(filtered_word_dict)
            html = word_cloud.render_embed()
            html_with_scroll = f"""
            <div style="width: 100%; height: 600px; overflow: auto;">
                {html}
            </div>
            """
            st.components.v1.html(html_with_scroll, height=600)
        elif graph_type == "词频前20柱状图":
            bar_chart = draw_bar_chart(filtered_word_dict)
            st.plotly_chart(bar_chart)
        elif graph_type == "折线图":
            line_chart = draw_line_chart(filtered_word_dict)
            st.plotly_chart(line_chart)
        elif graph_type == "饼图":
            pie_chart = draw_pie_chart(filtered_word_dict)
            st.plotly_chart(pie_chart)
        elif graph_type == "箱线图":
            boxplot_chart = draw_boxplot_chart(filtered_word_dict)
            st.pyplot(boxplot_chart)
        elif graph_type == "散点图":
            scatter_chart = draw_scatter_chart(filtered_word_dict)
            st.plotly_chart(scatter_chart)
        elif graph_type == "雷达图":
            radar_chart = draw_radar_chart(filtered_word_dict)
            st.plotly_chart(radar_chart)


if __name__ == "__main__":
    main()
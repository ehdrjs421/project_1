import os
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from utils import helpers
## 데이터 불러오기
root_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
data_path = os.path.join(root_path, "project1", "data","final")
path = os.path.join(data_path, "final_df.csv")

df = helpers.load_and_cast_final_df(path)

df = df[(df['price'] > 0) & df['freight_value'].notna()].copy()

# 배송 지연 여부
df['is_delayed'] = (
    df['total_day']
    .astype(str)
    .str.strip()
    .str.replace('–', '-', regex=False)
    .eq('20day+')
)

# 가격 대비 운임비 비율
df['freight_ratio'] = df['freight_value']

# 배송 상태별 분위수
q25 = df.groupby('is_delayed')['freight_ratio'].transform(lambda x: x.quantile(0.25))
q75 = df.groupby('is_delayed')['freight_ratio'].transform(lambda x: x.quantile(0.75))

df['freight_ratio_25_group'] = np.where(
    df['freight_ratio'] <= q25, 'Bottom 25%',
    np.where(df['freight_ratio'] >= q75, 'Top 25%', 'Middle')
)

df_25 = df[df['freight_ratio_25_group'] != 'Middle']

summary_25 = (
    df_25
    .groupby(['is_delayed', 'freight_ratio_25_group'])
    .agg(
        review_score=('review_score', 'mean'),
        count=('review_score', 'count')
    )
    .reset_index()
)

print(summary_25)
plt.figure(figsize=(9, 6))

ax = sns.barplot(
    data=summary_25,
    x='freight_ratio_25_group',
    y='review_score',
    hue='is_delayed',
    alpha=0.65
)

sns.pointplot(
    data=summary_25,
    x='freight_ratio_25_group',
    y='review_score',
    hue='is_delayed',
    dodge=0.4,
    markers='o',
    linestyles='-',
    errorbar=None,
    legend=False
)

# 값 라벨
for container in ax.containers:
    ax.bar_label(container, fmt='%.2f', padding=3, fontsize=10)

plt.title(
    'Review Score by Freight Ratio (Top/Bottom 15%)\nSeparated by Delivery Delay',
    fontsize=14
)
plt.xlabel('Freight Ratio Group')
plt.ylabel('Average Review Score')
plt.ylim(0, 5)
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
helpers.save_figure("배송 20일 기준 운임비에 따른 만족도 차이.png")

plt.show()


import os
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from utils import helpers
## 데이터 불러오기
root_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
data_path = os.path.join(root_path, "project1", "data","final")
path = os.path.join(data_path, "final_df.csv")

final_df = helpers.load_and_cast_final_df(path)

se_states = ['SP', 'RJ', 'ES', 'MG']
final_df['region_group'] = final_df['customer_state'].apply(lambda x: 'South-East' if x in se_states else 'Others')

# 2. 20일 이상 여부 플래그 생성
final_df['is_over_20days'] = final_df['total_day'] == '20day+'

# 3. 배송 기간 구간 설정 (5일 단위)
bins = [0, 5, 10, 15, 20, 30,50]
labels = ['0-5d', '5-10d', '10-15d', '15-20d', '20-30d', '30d+']
final_df['delivery_range'] = pd.cut(final_df['total_delivery_time'].dt.days, bins=bins, labels=labels)

# 지역별/배송기간구간별 평균 별점 계산
region_score_analysis = final_df.groupby(['region_group', 'delivery_range'])['review_score'].mean().unstack()

# 시각화: 지역별 배송 기간에 따른 별점 하락 추이
plt.figure(figsize=(12, 6))
sns.lineplot(data=final_df, x='delivery_range', y='review_score', hue='region_group', marker='o')
plt.axvline(x='15-20d', color='red', linestyle='--', label='20 Days Threshold')
plt.title('Review Score Drop: South-East vs Others')
plt.ylabel('Average Review Score')
plt.xlabel('Total Delivery Time (Days)')
plt.legend()
helpers.save_figure("남동부 지역과 그 외 지역 배송 기간 별 만족도 차이.png")
plt.show()

## plt.show 이전에사용하여 이미지 저장


bins = [0, 5, 10, 15, 20, 30, 50]
labels = ['0-5d', '5-10d', '10-15d', '15-20d', '20-30d', '30d+']

final_df['delivery_range'] = pd.cut(
    final_df['total_delivery_time'].dt.days,
    bins=bins,
    labels=labels
)

# 배송 기간 구간별 평균 만족도
delivery_score = (
    final_df
    .groupby('delivery_range', observed=True)['review_score']
    .mean()
    .reset_index()
    .sort_values('delivery_range')
)
delivery_score['score_diff'] = delivery_score['review_score'].diff()

fig, ax1 = plt.subplots(figsize=(12, 6))

# 🔹 Line plot: 평균 만족도
sns.lineplot(
    data=delivery_score,
    x='delivery_range',
    y='review_score',
    marker='o',
    ax=ax1
)
ax1.set_ylabel('Average Review Score')
ax1.set_xlabel('Delivery Time Range')
ax1.set_title('Average Review Score and Score Change by Delivery Time')

# 🔹 두 번째 y축
ax2 = ax1.twinx()

# Bar plot: 만족도 변화량
sns.barplot(
    data=delivery_score,
    x='delivery_range',
    y='score_diff',
    alpha=0.3,
    ax=ax2
)
ax2.set_ylabel('Change in Review Score')

# 기준선
ax2.axhline(0, color='gray', linestyle='--')

plt.tight_layout()
helpers.save_figure("배송기간별_만족도_및_변화량.png")
plt.show()

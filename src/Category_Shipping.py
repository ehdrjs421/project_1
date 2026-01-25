import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import koreanize_matplotlib
from utils import helpers

from google.colab import drive
drive.mount('/content/drive')

## ==============================
## 데이터 불러오기
path = '/content/drive/MyDrive/송파_새싹2기/프로젝트1/data/'
data1 = pd.read_csv(path+'final_df_0121.csv')
print(data1.shape)
data1.head(5)

data1.dtypes
data1.isnull().sum()


## ==============================
## 날짜 데이터 확인

# 날짜 관련 컬럼만 추출 
date_cols = [
    'order_delivered_carrier_date',
    'order_purchase_timestamp',
    'order_delivered_customer_date',
    'order_estimated_delivery_date'
]

for col in date_cols:
    data1[col] = pd.to_datetime(data1[col])

# 시간 간격을 나타내는 컬럼 
data1['total_delivery_time'] = pd.to_timedelta(data1['total_delivery_time'], errors='coerce')
data1['delay_days'] = pd.to_timedelta(data1['delay_days'], errors='coerce')


# 배송 예상 소요일 계산
# estimate = Olist에서 고객에게 제공한 도착 예정일
# 배송 예상 소요일 = 예정 도착일(estimate) - 주문일(purchase) 
data1['estimate_days'] = data1['order_estimated_delivery_date'] - data1['order_purchase_timestamp']


## ==============================
## 20일 전후 기준으로 데이터 분리

# 20일 이하
data_bf20 = data1[data1['total_day'] != '20day+'].reset_index(drop=True)
data_bf20.head()

# 20일 초과
data_aft20 = data1[data1['total_day'] == '20day+'].reset_index(drop=True)
data_aft20.head()


## ==============================
## 카테고리별로 배송이 20일 이상 걸린 주문의 비율 확인 

# 배송 소요일수 날짜 값만 뽑기 
data1['total_day_only'] = data1['total_delivery_time'].dt.days
data_aft20['total_day_only'] = data_aft20['total_delivery_time'].dt.days

# 전체 데이터에서, 카테고리별 배송 소요 일수의 평균/중앙값
data_def_df = data1.groupby('product_category_name_english')['total_day_only'].agg(['count','mean','max','min','median']).round(2).sort_values('median', ascending=False).rename(columns={
        'count': 'all_count', 'mean': 'all_mean', 'median': 'all_median', 'max': 'all_max', 'min': 'all_min'}).reset_index()

# 배송이 20일 이상 걸린 경우에서, 카테고리별 배송 소요 일수의 평균/중앙값
data_aft20_def_df = data_aft20.groupby('product_category_name_english')['total_day_only'].agg(['count','mean','max','min','median']).round(2).sort_values('median', ascending=False).rename(columns={
        'count': 'aft20_count', 'mean': 'aft20_mean', 'median': 'aft20_median', 'max': 'aft20_max', 'min': 'aft20_min'}).reset_index()

# 두 데이터 join
data_category_days = pd.merge(data_def_df, data_aft20_def_df, how='left', on='product_category_name_english')
data_category_days


# 카테고리별로 전체 배송 중 20일 넘게 걸린 건의 비율=20일 넘게 걸린 배송 건수/전체 배송 건수
data_category_days ['after20_ratio'] = data_category_days['aft20_count'] / data_category_days['all_count']
cols = ['product_category_name_english','aft20_count', 'after20_ratio', 'aft20_mean', 'aft20_max', 'aft20_min', 'aft20_median']

clean_df = ( data_category_days[cols].dropna())
clean_df
# => office_furniture가 39.9%로 배송에 20일 이상 소요된 경우가 가장 많음


## ==============================
## 배송 지연 상위 카테고리들 확인 

# 전체 배송 건수 중 20일 뒤에 배송된 건수가 100회 이상인 카테고리만 남김
category_list = clean_df[(clean_df['aft20_count'] > 100)][['product_category_name_english','after20_ratio','aft20_count','aft20_median']].reset_index(drop=True)
category_list

# 비율이 높은 것부터 내림차순 정렬
category_list_sorted = category_list.sort_values(by='after20_ratio', ascending=False).reset_index(drop=True)
category_list_sorted['after20_ratio_pct'] = (category_list_sorted['after20_ratio'].mul(100).round(1).astype(str) + '%')
category_list_sorted[['product_category_name_english','after20_ratio_pct']]


## ==============================
## 전자기기 제품들만 뽑아서 확인
# 'electronics', 'telephony', 'computers_accessories'

cat_elec = ['electronics','telephony', 'computers_accessories']

# 전체 데이터에서 전자기기 관련 카테고리들만 추출
only_cat_elec = data1[data1['product_category_name_english'].isin(cat_elec)].reset_index(drop=True)

# 20일 이후 데이터에서 전자기기 관련 카테고리들만 추출
only_cat_elec_aft20 = data_aft20[data_aft20['product_category_name_english'].isin(cat_elec)].reset_index(drop=True)


## 배송 소요시간의 차이 보기
only_cat_elec['handling_time'] = (only_cat_elec['order_delivered_carrier_date'] - only_cat_elec['order_purchase_timestamp']).dt.total_seconds() / (24 * 3600)
only_cat_elec['is_over_20days'] = only_cat_elec['total_day'] == '20day+'

# 시각화
# 20일 이상 배송 여부에 따른 Handling Time 평균 비교
handling_analysis = only_cat_elec.groupby('is_over_20days')['handling_time'].agg(['mean', 'median', 'max', 'count']).reset_index()

print("--- 최종 배송 기간(20일 기준)에 따른 출고 소요 시간 비교 ---")
print(handling_analysis)
plt.figure(figsize=(10, 5))

sns.kdeplot(data=only_cat_elec[only_cat_elec['is_over_20days'] == False], x='handling_time', label='Under 20 Days (Normal)', fill=True, color='skyblue')
sns.kdeplot(data=only_cat_elec[only_cat_elec['is_over_20days'] == True], x='handling_time', label='Over 20 Days (Delayed)', fill=True, color='salmon')

# 평균선 표시
plt.axvline(only_cat_elec[only_cat_elec['is_over_20days'] == False]['handling_time'].mean(), color='blue', linestyle='--', label='Under 20 Avg')
plt.axvline(only_cat_elec[only_cat_elec['is_over_20days'] == True]['handling_time'].mean(), color='red', linestyle='--', label='Over 20 Avg')
plt.title('전자기기 카테고리의 출고 시간 분포', fontsize=15)

# 평균값 텍스트 표시
mean_normal = handling_analysis.loc[0, 'mean']
mean_delayed = handling_analysis.loc[1, 'mean']
plt.text(mean_normal, plt.ylim()[1]*0.9, f'{mean_normal:.1f} days', color='blue', ha='left')
plt.text(mean_delayed, plt.ylim()[1]*0.8, f'{mean_delayed:.1f} days', color='red', ha='left')

plt.xlabel('Days from Purchase to Carrier Date')
plt.ylabel('Density')
plt.legend()
plt.xlim(0, 30) # 0-30일로 제한
helpers.save_figure("전자기기 출고시간 분포.png")
plt.show()

# 전자기기 카테고리 배송일수에 따른 별점 차이
only_cat_elec.groupby('is_over_20days')['review_score'].agg(['mean'])


## ==============================
## Office furniture 제품들만 뽑아서 확인

# 전체 데이터에서 office 카테고리들만 추출
only_office_furniture = data1[data1['product_category_name_english']=='office_furniture'].reset_index(drop=True)

## 배송 소요시간의 차이 보기
only_office_furniture['handling_time'] = (only_office_furniture['order_delivered_carrier_date'] - only_office_furniture['order_purchase_timestamp']).dt.total_seconds() / (24 * 3600)
only_office_furniture['is_over_20days'] = only_office_furniture['total_day'] == '20day+'

# 시각화
# 20일 이상 배송 여부에 따른 Handling Time 평균 비교
handling_analysis = only_office_furniture.groupby('is_over_20days')['handling_time'].agg(['mean', 'median', 'max', 'count']).reset_index()

print("--- 최종 배송 기간(20일 기준)에 따른 출고 소요 시간 비교 ---")
print(handling_analysis)
plt.figure(figsize=(10, 5))

sns.kdeplot(data=only_office_furniture[only_office_furniture['is_over_20days'] == False], x='handling_time', label='Under 20 Days (Normal)', fill=True, color='skyblue')
sns.kdeplot(data=only_office_furniture[only_office_furniture['is_over_20days'] == True], x='handling_time', label='Over 20 Days (Delayed)', fill=True, color='salmon')

# 평균선 표시
plt.axvline(only_office_furniture[only_office_furniture['is_over_20days'] == False]['handling_time'].mean(), color='blue', linestyle='--', label='Under 20 Avg')
plt.axvline(only_office_furniture[only_office_furniture['is_over_20days'] == True]['handling_time'].mean(), color='red', linestyle='--', label='Over 20 Avg')
plt.title('사무용 가구 카테고리의 출고 시간 분포', fontsize=15)

# 평균값 텍스트 표시
mean_normal = handling_analysis.loc[0, 'mean']
mean_delayed = handling_analysis.loc[1, 'mean']
plt.text(mean_normal, plt.ylim()[1]*0.9, f'{mean_normal:.1f} days', color='blue', ha='left')
plt.text(mean_delayed, plt.ylim()[1]*0.8, f'{mean_delayed:.1f} days', color='red', ha='left')

plt.xlabel('Days from Purchase to Carrier Date')
plt.ylabel('Density')
plt.legend()
plt.xlim(0, 30) # 0-30일로 제한
helpers.save_figure("사무용가구 출고시간 분포.png")
plt.show()
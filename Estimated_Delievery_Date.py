import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import koreanize_matplotlib


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

# 배송일 20일 이하의 리뷰 별점 평균
data_bf20['total_day'].value_counts() #normalize=True
print(data_bf20['review_score'].mean().round(2))
# => 평균 별점 4.22
# => 대부분 5점(60% 이상)

# 배송일 20일 초과의 리뷰 별점 평균 
data_aft20['review_score'].value_counts() #normalize=True
print(data_aft20['review_score'].mean().round(2))
# => 평균 별점 3.08
# => 1점(32%)/5점(31%) 두 값이 극단적으로 나타남


## ==============================
## 전체 데이터에서 배송 예상 소요일의 분포 
# day 단위로 변환하고 개수 count
estimate_days_cnt = (data1['estimate_days'].dt.days.value_counts().sort_index())

plt.figure()

plt.plot(estimate_days_cnt.index, estimate_days_cnt.values,label='Estimated Delivery Days')
plt.axvline(x=20, color='red', linestyle='--', label='20 Days')

plt.xlabel('Days')
plt.ylabel('Count')
plt.title('Distribution of Delivery Days')
plt.legend()
plt.show()
# => 전체 데이터를 봤을 때, 배송 예상 소요일의 분포는 2~3주


## 배송일수 20일 초과한 경우만 봤을 때, 배송 예상 소요일의 분포  
from matplotlib import lines

# day 단위로 변환하고 개수 count
total_days_cnt = (data_aft20['total_delivery_time'].dt.days.value_counts().sort_index())
estimate_days_cnt = (data_aft20['estimate_days'].dt.days.value_counts().sort_index())

plt.figure()

plt.plot(estimate_days_cnt.index, estimate_days_cnt.values,label='Estimated Delivery Days')
plt.axvline(x=20, color='red', linestyle='--', label='20 Days')

plt.xlabel('Days')
plt.ylabel('Count')
plt.title('Distribution of Delivery Days')
plt.legend()
plt.show()
# => 배송 기간이 20일 이상이었던 경우, 대부분의 사람들이 배송 예정 기간을 20~40일 사이로 안내 받음


## ==============================
## 배송 예상 소요일 안내에 따른 만족도
# 배송기간 20일 넘을 것이라고 안내 받은 경우의 비율 
data_aft20_estY = data_aft20[(data_aft20['estimate_days'].dt.days > 20)]
review_ratio_Y = data_aft20_estY['review_score'].value_counts(normalize=True)
review_ratio_Y

# 배송기간 20일 넘기지 않을 것이라고 안내받음
data_aft20_estN = data_aft20[(data_aft20['estimate_days'].dt.days <= 20)]
review_ratio_N = data_aft20_estN['review_score'].value_counts(normalize=True)
review_ratio_N

# 차트
# 색상 지정
color_map = {
    1: '#d73027',
    2: '#fc8d59',
    3: '#fee08b',
    4: '#91bfdb',
    5: '#4575b4'
}

colors_Y = [color_map[int(i)] for i in review_ratio_Y.index]
plt.figure()
plt.pie(review_ratio_Y.values, labels=review_ratio_Y.index.astype(int), autopct='%.1f%%', startangle=90, colors=colors_Y)
plt.title('리뷰 별점 분포 (예정 배송 소요일 > 20)')
plt.show()

colors_N = [color_map[int(i)] for i in review_ratio_N.index]
plt.figure()
plt.pie(review_ratio_N.values, labels=review_ratio_N.index.astype(int), autopct='%.1f%%', startangle=90, colors=colors_N)
plt.title('리뷰 별점 분포 (예정 배송 소요일 <= 20)')
plt.show()
# => 배송이 20일 이상 걸리더라도, 사전에 공지가 된다면 만족도를 개선할 수 있을 것.


## ==============================
## 배송 예상 소요일 안내에 따른 만족도
# 예상 배송일과 실제 배송일 차이에 따른 고객 만족도 
data_aft20['del_diff'] = data_aft20['estimate_days'].dt.days - data_aft20['total_delivery_time'].dt.days
del_diff_review_mean = (data_aft20.groupby('del_diff')['review_score'].mean().sort_index())

# 차트
# 색상 지정
colors = ['steelblue' if i >= 0 else 'salmon' for i in del_diff_review_mean.index]

plt.figure()
plt.scatter(del_diff_review_mean.index, del_diff_review_mean.values, color=colors)
plt.axvline(x=0, linestyle='--', label='On-time', color='gray')

plt.xlim(-30, 30)
plt.xlabel('Date Difference')
plt.ylabel('Review Rate')
plt.title('예상배송일과 실제배송일 차이에 따른 고객 만족도 ')
plt.legend()
plt.show()

# 각 평균값 
diff[(diff['del_diff']>=-30) & (diff['del_diff']<0)]['review_score'].mean()
diff[(diff['del_diff']>0) & (diff['del_diff']<=30)]['review_score'].mean()
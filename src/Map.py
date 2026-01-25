import os
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from folium.plugins import HeatMap
from utils import helpers
## 데이터 불러오기
root_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
data_path = os.path.join(root_path, "project1", "data","final")
path = os.path.join(data_path, "final_df.csv")

final_df = helpers.load_and_cast_final_df(path)

map_df = pd.merge(
    final_df,
    geo_small,
    left_on='customer_zip_code_prefix',
    right_on='geolocation_zip_code_prefix',
    how='left'
)

# 좌표가 없는 행은 지도에 찍을 수 없으므로 제거
map_df = map_df.dropna(subset=['geolocation_lat', 'geolocation_lng'])

# delay_days 수치화 (Timedelta -> 정수형 days)
map_df['delay_days_numeric'] = map_df['delay_days'].apply(lambda x: x.days if hasattr(x, 'days') else x)
map_df.columns

# 브라질 중심부 설정
m = folium.Map(location=[-14.2350, -51.9253], zoom_start=4)

# 샘플링
sample_df = map_df.sample(n=min(7000, len(map_df)))

# 마커 클러스터 추가
marker_cluster = MarkerCluster().add_to(m)

for _, row in sample_df.iterrows():
    # --- [기준 1: 배송 지연 여부] ---
    # 지연(빨간색), 정시/조기(파란색)
    delay_color = 'red' if row['delay_days_numeric'] > 0 else 'blue'

    # --- [기준 2: 20일 이상 소요 여부] ---
    # 20+인 경우 테두리나 아이콘 내부색으로 구분 가능
    # 여기서는 기준 2를 강조하기 위해 20+인 경우 마커 크기를 키우거나 투명도를 조절해 보겠습니다.
    is_long_delivery = row['total_day'] == '20day+'
    radius = 6 if is_long_delivery else 3
    fill_opacity = 0.8 if is_long_delivery else 0.4

    folium.CircleMarker(
        location=[row['geolocation_lat'], row['geolocation_lng']],
        radius=radius,
        color=delay_color,
        fill=True,
        fill_color=delay_color,
        fill_opacity=fill_opacity,
        popup=(f"Order ID: {row['order_id']}<br>"
              #  f"Status: {row['order_status']}<br>"
               f"Delay: {row['delay_days']} days<br>"
               f"Total Group: {row['total_day']}"),
    ).add_to(marker_cluster)

# 지도 출력
m

delay_only_df = map_df[map_df['delay_days_numeric'] > 0].copy()

# 1. 지도 생성 (줌 조절 및 이동 제한 옵션 추가)
m_fixed = folium.Map(
    location=[-14.2350, -51.9253],
    zoom_start=4,
    min_zoom=4,     # 너무 축소되지 않게 고정
    max_zoom=10,    # 너무 확대되지 않게 제한 (선택 사항)
    zoom_control=True
)

# 2. 샘플링 (데이터가 수만 건이면 브라우저가 멈출 수 있으므로 3,000건 권장)
sample_df = map_df.sample(n=min(3000, len(map_df)))
sample_size = min(3000, len(delay_only_df))
delay_sample = delay_only_df.sample(n=sample_size, random_state=42)

for _, row in delay_only_df.iterrows():
# for _, row in sample_df.iterrows():
    # 기준 1: 지연 여부 (빨간색: 지연, 파란색: 정시/조기)
    dot_color = 'red' if row['delay_days_numeric'] > 0 else 'blue'

    # 기준 2: 20일 이상 소요 여부 (20+일 때 점을 더 크고 진하게)
    is_long = row['total_day'] == '20+'
    dot_radius = 5 if is_long else 2
    dot_opacity = 0.9 if is_long else 0.5

    # MarkerCluster를 사용하지 않고 바로 지도(m_fixed)에 추가
    folium.CircleMarker(
        location=[row['geolocation_lat'], row['geolocation_lng']],
        radius=dot_radius,
        color=dot_color,
        fill=True,
        fill_color=dot_color,
        fill_opacity=dot_opacity,
        weight=1, # 테두리 두께
        popup=f"Delay: {row['delay_days_numeric']}d | Total: {row['total_day']}"
    ).add_to(m_fixed)

# 코랩에서 바로 확인
m_fixed



# 1. 지연이 발생한 데이터만 필터링
delay_data = map_df[map_df['delay_days_numeric'] > 0][['geolocation_lat', 'geolocation_lng']]

# 2. 지도 생성 (브라질 중심 고정)
m_heatmap = folium.Map(location=[-14.2350, -51.9253], zoom_start=4)

# 3. 히트맵 추가
HeatMap(delay_data, radius=5, blur=5, max_zoom=1).add_to(m_heatmap)

# 코랩에서 바로 확인
m_heatmap
####################################################

# 1. 판매자 우편번호를 기준으로 좌표 결합
map_df = pd.merge(
    map_df,
    geo_small,
    left_on='seller_zip_code_prefix',
    right_on='geolocation_zip_code_prefix',
    how='left',
    suffixes=('', '_seller') # 고객 좌표와 판매자 좌표 구분
)

# 컬럼명 정리 (보기 편하게)
map_df = map_df.rename(columns={
    'geolocation_lat_seller': 'seller_lat',
    'geolocation_lng_seller': 'seller_lng'
})
map_df = map_df.dropna(subset=['geolocation_lat', 'geolocation_lng','seller_lat', 'seller_lng'])
# 지연된 데이터만 추출 및 결측치 제거
# delay_only_df = map_df[map_df['delay_days_numeric'] > 0].dropna(subset=['geolocation_lat', 'geolocation_lng', 'seller_lat', 'seller_lng']).copy()

# 1. 중복된 컬럼이 있는지 확인하고 하나만 남기기
# 만약 동일한 이름의 컬럼이 여러 개라면 첫 번째 것만 선택합니다.
map_df = map_df.loc[:, ~map_df.columns.duplicated()]

# 2. 위도/경도 값을 확실하게 숫자(float) 타입으로 변환
# 에러가 난 seller_lat을 포함하여 모든 좌표 컬럼을 변환합니다.
geo_cols = ['geolocation_lat', 'geolocation_lng', 'seller_lat', 'seller_lng']

for col in geo_cols:
    # 숫자로 변환하되, 변환할 수 없는 값(문자열 등)은 NaN으로 처리
    map_df[col] = pd.to_numeric(map_df[col], errors='coerce')

# 3. 변환 후 발생한 결측치(NaN) 행 제거 (지도를 그릴 수 없으므로)
map_df = map_df.dropna(subset=geo_cols)

# 4. 이제 다시 샘플링하여 지도 그리기
delay_only_df = map_df[map_df['delay_days_numeric'] > 0].copy()

# 브라질 중심 고정
m_logistics = folium.Map(location=[-14.2350, -51.9253], zoom_start=4, min_zoom=4)

# 지연 데이터 샘플링 (시각적 과부하 방지를 위해 1,000~1,500세트 추천)
sample_size = min(1000, len(delay_only_df))
logistics_sample = map_df.sample(n=sample_size, random_state=42)

for _, row in logistics_sample.iterrows():
    # 1. 판매자 위치 (출발지)
    folium.CircleMarker(
        location=[row['seller_lat'], row['seller_lng']],
        radius=3,
        color='orange',
        fill=True,
        fill_color='orange',
        fill_opacity=0.7,
        popup=f"Seller ID: {row['seller_id']}<br>State: {row['seller_state']}"
    ).add_to(m_logistics)

    # 2. 고객 위치 (지연 도착지)
    # 20일 이상 소요 여부에 따라 고객 점 크기 조절
    is_long = row['total_day'] == '20day+'
    folium.CircleMarker(
        location=[row['geolocation_lat'], row['geolocation_lng']],
        radius=6 if is_long else 3,
        color='red',
        fill=True,
        fill_color='red',
        fill_opacity=0.6,
        popup=f"Delay: {row['delay_days_numeric']}d<br>Total: {row['total_day']}"
    ).add_to(m_logistics)

m_logistics

# 1. 지도 생성 (브라질 중심)
m_lines = folium.Map(location=[-14.2350, -51.9253], zoom_start=4)

# 2. 지연된 데이터 중 최악의 지연 사례 100건 샘플링
line_sample = delay_only_df.sort_values(by='delay_days_numeric', ascending=False).head(100)

for _, row in line_sample.iterrows():
    # 좌표 추출 (float 형변환 확인)
    seller_coords = [float(row['seller_lat']), float(row['seller_lng'])]
    customer_coords = [float(row['geolocation_lat']), float(row['geolocation_lng'])]

    # --- 판매자 점 (시작점: 주황색) ---
    folium.CircleMarker(
        location=seller_coords,
        radius=3,
        color='orange',
        fill=True,
        popup=f"Seller: {row['seller_id']}"
    ).add_to(m_lines)

    # --- 고객 점 (도착점: 빨간색) ---
    folium.CircleMarker(
        location=customer_coords,
        radius=3,
        color='red',
        fill=True,
        popup=f"Delay: {row['delay_days_numeric']} days"
    ).add_to(m_lines)

    # --- 판매자와 고객을 선으로 연결 ---
    # 지연 일수가 길수록 선을 더 굵게 표현하여 가독성 높임
    weight = 1 + (row['delay_days_numeric'] / 10)
    folium.PolyLine(
        locations=[seller_coords, customer_coords],
        weight=min(weight, 5), # 최대 굵기 제한
        color='black',
        opacity=0.3,
        tooltip=f"Route: {row['seller_state']} -> {row['customer_state']}"
    ).add_to(m_lines)

m_lines
## plt.show 이전에사용하여 이미지 저장
helpers.save_figure("저장명.png")

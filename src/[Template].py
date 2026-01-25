import os
from utils import helpers
## 데이터 불러오기
root_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
data_path = os.path.join(root_path, "project1", "data","final")
path = os.path.join(data_path, "final_df.csv")

final_df = helpers.load_and_cast_final_df(path)

## plt.show 이전에사용하여 이미지 저장
helpers.save_figure("저장명.png")

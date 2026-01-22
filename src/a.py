from utils import helpers
import os

root_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
data_path = os.path.join(root_path, "project1", "data","final")
path = os.path.join(data_path, "final_df.csv")

final_df = helpers.load_and_cast_final_df(path)
final_df.info()
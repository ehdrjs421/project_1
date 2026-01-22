import matplotlib.pyplot as plt
import seaborn as sns

def set_korean_font():
    """
    koreanize-matplotlib을 사용하여 한글 폰트 설정을 수행합니다.
    """
    try:
        import koreanize_matplotlib
        print("koreanize-matplotlib 적용 완료")
    except ImportError:
        print("koreanize-matplotlib이 설치되어 있지 않습니다. pip install koreanize-matplotlib 을 실행해 주세요.")

def fix_path():
    """
    노트북에서 src 폴더를 임포트할 수 있도록 프로젝트 루트 경로를 설정합니다.
    """
    import sys
    import os
    root_path = os.path.abspath(os.path.join(os.getcwd(), '..'))
    if root_path not in sys.path:
        sys.path.append(root_path)
    print(f"Project root added to sys.path: {root_path}")

def save_fig(fig_id, tight_layout=True, fig_extension="png", resolution=300):
    """
    reports/figures 폴더에 그래프를 저장합니다.
    """
    from pathlib import Path
    path = Path("reports") / "figures" / f"{fig_id}.{fig_extension}"
    if tight_layout:
        plt.tight_layout()
    plt.savefig(path, format=fig_extension, dpi=resolution)
    
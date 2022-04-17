from pathlib import Path
import pandas as pd

cwd = Path.cwd()
data = pd.read_csv(cwd/'src'/'data'/'processed'/'train.csv')
print(data.shape)

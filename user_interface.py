from pyclbr import Class
from scrape import ExtractData
import pandas as pd
import os

c = ExtractData(primary_option='gg')


d = c.scrape()

for i,j in d.items():
    file_path = os.path.expanduser(f'~/Downloads/{i}.csv')
    j.to_csv(file_path, index=False)


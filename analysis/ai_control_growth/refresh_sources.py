import requests,concurrent.futures,json,argparse
from pathlib import Path
from bs4 import BeautifulSoup
parser=argparse.ArgumentParser();parser.add_argument('--cache',default='/tmp/control-variant-sources');args=parser.parse_args()
root=Path(args.cache);root.mkdir(parents=True,exist_ok=True)
ids=['2312.06942','2504.10374','2510.09462','2511.02997','2604.15384','2605.26047','2606.06529','2606.11998','2609.19587v2','2605.09684','2609.30217','2602.20628','2504.18530','2512.22154']
def fetch(pid):
 url='https://arxiv.org/html/'+pid;r=requests.get(url,timeout=90);r.raise_for_status();(root/(pid+'.html')).write_text(r.text);s=BeautifulSoup(r.text,'html.parser');tables=[];figures=[]
 for el in s.select('figure'):
  c=el.find('figcaption');caption=c.get_text(' ',strip=True) if c else ''
  if el.select('table'):
   rows=[]
   for row in el.select('tr'):
    cells=[{'text':cell.get_text(' ',strip=True),'rowspan':cell.get('rowspan',1),'colspan':cell.get('colspan',1)} for cell in row.find_all(['th','td'],recursive=False)]
    if cells:rows.append(cells)
   tables.append(dict(id=el.get('id'),caption=caption,rows=rows))
  else:figures.append(dict(id=el.get('id'),caption=caption,images=[dict(src=i.get('src'),alt=i.get('alt')) for i in el.select('img')]))
 out=dict(url=url,tables=tables,figures=figures);(root/(pid+'.json')).write_text(json.dumps(out,indent=2));return pid,[(t['id'],t['caption'][:160],len(t['rows'])) for t in tables],[(f['id'],f['caption'][:120]) for f in figures[:8]]
for result in concurrent.futures.ThreadPoolExecutor(max_workers=6).map(fetch,ids):print(json.dumps(result))

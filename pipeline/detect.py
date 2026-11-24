# Détecteur DIGED NEWS : 3 rayons (monde/économie, sport, tendances US) ; affiche les meilleurs sujets de chaque rayon.
import urllib.request, xml.etree.ElementTree as ET, email.utils, datetime as dt, re, html, sys
UA={'User-Agent':'Mozilla/5.0'}
def get(u): return ET.fromstring(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=20).read())
now=dt.datetime.now(dt.timezone.utc)
def items(u, src, maxh):
    out=[]
    try:
        for it in get(u).iter('item'):
            p=it.findtext('pubDate'); t=html.unescape((it.findtext('title') or '').strip())
            if not p or not t: continue
            age=(now-email.utils.parsedate_to_datetime(p)).total_seconds()/3600
            if age<=maxh: out.append((src,t,round(age,1)))
    except Exception as e: print('ERR',src,str(e)[:60],file=sys.stderr)
    return out
WORLD={'BBC World':'https://feeds.bbci.co.uk/news/world/rss.xml','BBC US':'https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml','Guardian':'https://www.theguardian.com/world/rss','Al Jazeera':'https://www.aljazeera.com/xml/rss/all.xml','Politico':'https://rss.politico.com/politics-news.xml','Reuters (GN)':'https://news.google.com/rss/search?q=site:reuters.com+when:4h&hl=en-US&gl=US&ceid=US:en'}
SPORT={'ESPN':'https://www.espn.com/espn/rss/news','CBS Sports':'https://www.cbssports.com/rss/headlines/'}
print('=== TENDANCES US (Google Trends) ===')
ns={'ht':'https://trends.google.com/trending/rss'}
for it in list(get('https://trends.google.com/trending/rss?geo=US').iter('item'))[:12]:
    tr=it.findtext('ht:approx_traffic',namespaces=ns); n=it.find('ht:news_item',ns)
    if re.search(r'[一-鿿]', it.findtext('title') or ''): continue
    print(f"{tr:>6} | {it.findtext('title')} | {(n.findtext('ht:news_item_title',namespaces=ns) if n is not None else '')[:90]}")
for name,feeds,h in [('SPORT',SPORT,8),('MONDE / ÉCONOMIE',WORLD,4)]:
    print(f'=== {name} ===')
    allit=[x for s,u in feeds.items() for x in items(u,s,h)]
    for s,t,a in sorted(allit,key=lambda x:x[2])[:10]: print(f"{a:>4}h | {s:12s} | {t[:110]}")

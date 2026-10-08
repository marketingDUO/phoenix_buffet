"""Generate English static pages from the German pages and reviewed translations.
Run from the repository root. Requires beautifulsoup4 (build-time only).
"""
from pathlib import Path
from bs4 import BeautifulSoup, Doctype
from urllib.parse import urlsplit
import json,re,hashlib,xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[1];dist=root/'dist';(dist/'en').mkdir(exist_ok=True)
translations=json.loads((root/'scripts/translations-en.json').read_text())
origin='https://www.xn--phnix-buffet-5ib.de'
metadata={
'index.html':('Phönix Berlin: Chinese Buffet, Sushi & Live Grill in Prenzlauer Berg','Phönix Chinese Restaurant at Mühlenberg-Center in Berlin-Prenzlauer Berg: buffet, sushi and teppanyaki. Open daily from noon. 90 minutes of free parking.'),
'buffet.html':('Chinese Buffet in Berlin-Prenzlauer Berg | Phönix','Explore the Phönix buffet in Berlin-Prenzlauer Berg: lunch buffet, evening buffet, sushi and desserts. View prices, buffet hours and phone reservations.'),
'live-grill.html':('Teppanyaki & Live Grill in Berlin-Prenzlauer Berg | Phönix','Create your teppanyaki dish at Phönix Berlin: choose meat, fish, prawns and vegetables and enjoy them freshly grilled. Live Grill hours and buffet prices.'),
'sushi.html':('Sushi Buffet in Berlin-Prenzlauer Berg | Phönix','Enjoy maki, nigiri and vegetarian sushi as part of the buffet at Phönix Chinese Restaurant in Berlin-Prenzlauer Berg. Open daily from noon.'),
'speisekarte.html':('Menu & Buffet Prices in Berlin | Phönix Prenzlauer Berg','Phönix Berlin menu and buffet prices: lunch buffet from €15.90, evening buffet and Live Grill. Original German menu PDF. 90 minutes of free parking.'),
'kontakt.html':('Directions & Parking | Phönix Berlin-Prenzlauer Berg','Visit Phönix at Mühlenberg-Center, Greifswalder Straße 90, Berlin: M4, S-Bahn and bus connections, opening hours and 90 minutes of free parking.'),
'impressum.html':('Legal Notice | Phönix Chinese Restaurant Berlin','Legal notice and contact details for Phönix Chinese Restaurant in Berlin-Prenzlauer Berg, Greifswalder Straße 90, 10409 Berlin.'),
'datenschutz.html':('Privacy Policy | Phönix Chinese Restaurant Berlin','Privacy information for the Phönix Chinese Restaurant Berlin website and contact details for the data controller.')}
def url(name,en=False):return origin+('/en/' if en else '/')+('' if name=='index.html' else name)
def translate(t):
 key=t.strip()
 if not key:return t
 if key not in translations:raise ValueError('Missing English translation: '+key)
 return t[:len(t)-len(t.lstrip())]+translations[key]+t[len(t.rstrip()):]
def decorate(soup,name,en):
 for old in soup.select('.language-bar'):old.decompose()
 nav=soup.new_tag('nav',attrs={'class':'language-bar','aria-label':'Choose language' if en else 'Sprache wählen'})
 wrap=soup.new_tag('div',attrs={'class':'language-inner'})
 for language,label,is_en in [('de','Deutsch',False),('en','English',True)]:
  path=('/en/' if is_en else '/')+('' if name=='index.html' else name)
  a=soup.new_tag('a',href=path,attrs={'lang':language,'hreflang':language,'class':'language-link'})
  a.string=label
  if is_en==en:a['aria-current']='true';a['class']='language-link active'
  wrap.append(a)
 nav.append(wrap);soup.select_one('.site-header').insert(0,nav)
 for old in soup.find_all('link',rel='alternate',hreflang=True):old.decompose()
 for language,is_en in [('de',False),('en',True),('x-default',False)]:soup.head.append(soup.new_tag('link',attrs={'rel':'alternate','hreflang':language,'href':url(name,is_en)}))
for p in sorted(dist.glob('*.html')):
 de=BeautifulSoup(p.read_text(),'html.parser')
 for old in de.select('.language-bar'):old.decompose()
 en=BeautifulSoup(str(de),'html.parser');en.html['lang']='en'
 for node in list(en.find_all(string=True)):
  if isinstance(node,Doctype) or node.parent.name in ['script','style','title']:continue
  node.replace_with(translate(str(node)))
 for tag in en.find_all(True):
  for attr in ['alt','aria-label']:
   if tag.get(attr):tag[attr]=translate(tag[attr])
  for attr in ['src','href','poster']:
   val=tag.get(attr)
   if not val:continue
   if val=='/':tag[attr]='/en/'
   elif val.startswith('assets/') or val.startswith('styles.css') or val.startswith('script.js'):tag[attr]='../'+val
  if tag.get('srcset'):tag['srcset']=tag['srcset'].replace('assets/','../assets/')
  if tag.get('style'):tag['style']=tag['style'].replace("url('assets/","url('../assets/")
 title,description=metadata[p.name];en.title.string=title
 for tag in en.select('meta[name="description"],meta[property="og:description"],meta[name="twitter:description"]'):tag['content']=description
 for tag in en.select('meta[property="og:title"],meta[name="twitter:title"]'):tag['content']=title
 en.find('meta',property='og:url')['content']=url(p.name,True)
 en.find('meta',property='og:locale')['content']='en_GB'
 en.find('link',rel='canonical')['href']=url(p.name,True)
 for soup,is_en in [(de,False),(en,True)]:
  for tag in soup.find_all('script',type='application/ld+json'):
   graph=json.loads(tag.string)
   for entity in graph['@graph']:
    if entity['@type']=='WebSite':entity['inLanguage']=['de-DE','en']
    elif is_en and entity['@type']=='Restaurant':
     entity['description']='Chinese restaurant with buffet, sushi and teppanyaki at Mühlenberg-Center in Berlin-Prenzlauer Berg.'
     entity['servesCuisine']=['Chinese','Asian','Sushi','Teppanyaki']
     entity['amenityFeature'][0]['name']='Car park: first 90 minutes free'
    elif is_en and entity['@type']=='WebPage':
     entity.update({'@id':url(p.name,True)+'#webpage','url':url(p.name,True),'name':title,'description':description,'inLanguage':'en'})
    elif is_en and entity['@type']=='BreadcrumbList':
     for item in entity['itemListElement']:
      item['name']=translations[item['name']]
      item['item']=item['item'].replace(origin+'/',origin+'/en/',1)
   tag.string=json.dumps(graph,ensure_ascii=False,separators=(',',':'))
  decorate(soup,p.name,is_en)
 de_path=p;en_path=dist/'en'/p.name
 de_path.write_text(str(de));en_path.write_text(str(en))
# Sitemap includes language-paired canonical URLs.
ET.register_namespace('','http://www.sitemaps.org/schemas/sitemap/0.9');ET.register_namespace('xhtml','http://www.w3.org/1999/xhtml')
ns='http://www.sitemaps.org/schemas/sitemap/0.9';xns='http://www.w3.org/1999/xhtml';sitemap=ET.Element('{'+ns+'}urlset')
for name in metadata:
 for is_en in [False,True]:
  node=ET.SubElement(sitemap,'{'+ns+'}url');ET.SubElement(node,'{'+ns+'}loc').text=url(name,is_en)
  for language,alt_en in [('de',False),('en',True),('x-default',False)]:ET.SubElement(node,'{'+xns+'}link',{'rel':'alternate','hreflang':language,'href':url(name,alt_en)})
  ET.SubElement(node,'{'+ns+'}lastmod').text='2026-10-05'
ET.ElementTree(sitemap).write(dist/'sitemap.xml',encoding='utf-8',xml_declaration=True)
# Cache versions for the shared stylesheet and script.
for p in dist.rglob('*.html'):
 text=p.read_text()
 for asset in ['styles.css','script.js']:
  sha=hashlib.sha256((dist/asset).read_bytes()).hexdigest()[:12]
  text=re.sub(re.escape(asset)+r'(?:\?v=[a-f0-9]+)?',asset+'?v='+sha,text)
 p.write_text(text)
print('Generated 8 English pages with language-paired SEO metadata and sitemap.')

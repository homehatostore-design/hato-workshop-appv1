import json, re, requests
from bs4 import BeautifulSoup
from pathlib import Path

BASE = 'https://hatoworkshop.com/collections/%E4%B8%8A%E9%96%80%E5%B7%A5%E4%BD%9C%E5%9D%8A-%E5%88%B0%E6%A0%A1%E5%B7%A5%E4%BD%9C%E5%9D%8A'
URLS = [BASE] + [f'{BASE}?page={i}' for i in range(2, 8)]
HEADERS = {'User-Agent': 'Mozilla/5.0'}

def clean(s):
    return re.sub(r'\s+', ' ', s or '').strip()

def fetch_page(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text

def extract_items(html, url):
    soup = BeautifulSoup(html, 'html.parser')
    items = []
    for a in soup.select('a[href*="/products/"]'):
        href = a.get('href')
        if not href or '/products/' not in href:
            continue
        title = clean(a.get_text(' ', strip=True))
        img = a.find('img')
        image = ''
        if img:
            image = img.get('src') or img.get('data-src') or img.get('data-lazy-src') or ''
            if image.startswith('//'):
                image = 'https:' + image
            elif image.startswith('/'):
                image = 'https://hatoworkshop.com' + image
        if title:
            items.append({'name': title, 'url': 'https://hatoworkshop.com' + href, 'image': image, 'sourcePage': url})
    return items

seen = {}
for url in URLS:
    try:
        html = fetch_page(url)
        for it in extract_items(html, url):
            seen[it['url']] = it
    except Exception as e:
        print(f'Failed {url}: {e}')

items = list(seen.values())

for i in items:
    n = i['name']
    if '中秋' in n or '月' in n or '燈籠' in n:
        i['category'] = '中秋'
        i['theme'] = '中秋'
    elif '復活節' in n:
        i['category'] = '復活節'
        i['theme'] = '復活節'
    elif '萬聖節' in n:
        i['category'] = '萬聖節'
        i['theme'] = '萬聖節'
    elif '新年' in n or '招財' in n or '發財' in n:
        i['category'] = '新年'
        i['theme'] = '新年'
    elif '馬賽克' in n:
        i['category'] = '馬賽克'
        i['theme'] = '馬賽克'
    elif '永生花' in n or '壓花' in n or '乾花' in n or '浮游花' in n:
        i['category'] = '花藝'
        i['theme'] = '永生花'
    else:
        i['category'] = '其他'
        i['theme'] = ''
    i['price'] = None
    i['duration'] = ''
    i['description'] = ''
    i['audience'] = ''

workshops_path = Path('workshops.json')
helper_path = Path('helper.json')
workshops = []
for i in items:
    workshops.append({
        'name': i['name'],
        'price': i['price'],
        'image': i['image'],
        'description': i['description'],
        'duration': i['duration'],
        'category': i['category'],
        'theme': i['theme'],
        'audience': i['audience'],
        'source': i['url']
    })
helper = [
    {'name': x['name'], 'price': x['price'], 'image': x['image'], 'description': x['description'], 'duration': x['duration'], 'category': x['category'], 'theme': x['theme'], 'audience': x['audience'], 'source': x['source']}
    for x in workshops if x['theme'] == '中秋'
][:8]

workshops_path.write_text(json.dumps(workshops, ensure_ascii=False, indent=2), encoding='utf-8')
helper_path.write_text(json.dumps(helper, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Wrote {len(workshops)} workshops and {len(helper)} helper items')

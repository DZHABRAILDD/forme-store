"""Build this release from downloaded photographs; no generative image editing."""
import json, hashlib, shutil
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

root = Path(__file__).resolve().parent.parent
refs = root / 'references/nov20'
if (root/'src/seasonProducts.js').exists():
    raise SystemExit('This one-time migration is already applied. Use the saved originals for further image changes.')
def write(path, text): (root/path).write_text(text, encoding='utf-8')
def read(path): return (root/path).read_text('utf-8')

# Keep the current six original editorial photographs, now as hero slides.
editorial = read('src/editorial.js').replace('export const currentEditorials', 'export const heroPhotos', 1)
rows=[]
for number, source in enumerate([1,4,5,8,13,15],1):
    original=refs/f'editorial-{source}.jpg'
    target=root/f'public/images/editorials/collection-{number}.jpg'
    shutil.copyfile(original,target)
    w,h=Image.open(target).size
    rows.append(dict(id=f'collection-{number}',title=f'Кадр {number}',alt='Мужская коллекция: съёмка на фоне пустынного пейзажа',image=f'/images/editorials/collection-{number}.jpg',width=w,height=h,source='https://www.thefashionisto.com/massimo-dutti-2024-down-to-earth/',download=f'https://www.thefashionisto.com/wp-content/uploads/2024/12/Massimo-Dutti-2024-Down-to-Earth-{source:03}.jpg',photographer='Mark Kean',processing='Original JPEG bytes, no AI, no retouching',sha256=hashlib.sha256(original.read_bytes()).hexdigest()))
editorial += '\nexport const currentEditorials = '+json.dumps(rows,ensure_ascii=False,indent=2)+';\n'
editorial += "featuredBrands.push({name:'Tommy Hilfiger',image:'/images/brands/tommy.svg'},{name:'Ralph Lauren',image:'/images/brands/ralph.svg'});\n"
write('src/editorial.js',editorial)
shutil.copyfile(refs/'ralph-logo.svg',root/'public/images/brands/ralph.svg')
# Vector geometry of the flag emblem, without a font substitute.
write('public/images/brands/tommy.svg','<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 72"><path fill="#17243b" d="M0 0h120v72H0z"/><path fill="#fff" d="M4 16h56v40H4z"/><path fill="#bf1736" d="M60 16h56v40H60z"/></svg>')

def cutout(filename):
    im=Image.open(filename).convert('RGB'); pixels=np.asarray(im).astype(float)
    edge=max(3,im.width//35);left=np.median(pixels[:,:edge],axis=1);right=np.median(pixels[:,-edge:],axis=1)
    t=np.linspace(0,1,im.width)[None,:,None]
    bg=left[:,None,:]*(1-t)+right[:,None,:]*t
    mask=Image.fromarray((np.max(abs(pixels-bg),axis=2)>23).astype('uint8')*255)
    exterior=mask.copy();ImageDraw.floodfill(exterior,(0,0),128)
    mask=Image.fromarray(np.where(np.asarray(exterior)==128,0,255).astype('uint8')).filter(ImageFilter.GaussianBlur(.45))
    im=im.convert('RGBA');im.putalpha(mask);return im.crop(mask.getbbox())
def fitted(im,bounds):
    im=im.copy();im.thumbnail(bounds,Image.Resampling.LANCZOS);return im
products=[
 dict(id='merano-trousers',name='Брюки Loro Piana Merano',model='Merano Cashmere Sweatpants — P00897763',category='Брюки',color='Светло-серый',hex='#b2b3ae',price=12900,original='pants-merano.jpg',sourceUrl='https://www.mytheresa.com/at/en/men/loro-piana-merano-cashmere-sweatpants-grey-p00897763',referenceInstagram='https://www.instagram.com/triumph_mz/p/De38gVHBfds/',description='Трикотажные брюки Merano с поясом на кулиске и манжетами.',composition='100% кашемир',country='Италия'),
 dict(id='cd-icon-trousers',name='Брюки Dior CD Icon',model='CD Icon Drawstring Track Pants',category='Брюки',color='Серый',hex='#a8a8a6',price=14900,original='dior-gray-pants.jpg',sourceUrl='https://www.lyst.com/clothing/dior-sports-pants/',referenceInstagram='https://www.instagram.com/triumph_mz/p/De_8ak4iOmU/',description='Прямые спортивные брюки с кулиской на поясе и небольшой вышивкой CD Icon.'),
 dict(id='cd-icon-halfzip',name='Свитшот Dior CD Icon Half-Zip',model='513J635A0531_C988',category='Свитшоты',color='Графитовый',hex='#343436',price=16900,original='dior-top.jpg',sourceUrl='https://bordergara.com/products/dr-2505-0642',referenceInstagram='https://www.instagram.com/triumph_mz/p/De_8ak4iOmU/',description='Свитшот CD Icon с короткой молнией, воротником-стойкой и рельефной вышивкой.',neck='Воротник-стойка с короткой молнией',composition='100% хлопок',country='Италия'),
 dict(id='cap-tommy-logo',name='Кепка Tommy Hilfiger Logo',model='Cotton Logo Baseball Cap — 6941823-270',category='Кепки',color='Песочный',hex='#c9c4b7',price=5900,original='cap-stone.jpg',sourceUrl='https://manuals.plus/asin/B076KFH3YK',description='Хлопковая бейсболка с вышитым логотипом, изогнутым козырьком и регулировкой сзади.',composition='100% хлопок',sizes=['Единый']),
 dict(id='cap-shark-yachting',name='Кепка Paul & Shark Yachting',model='Nylon Yachting Cap — C0P7101',category='Кепки',color='Синий',hex='#3e5e9a',price=6900,original='cap-yachting.jpg',sourceUrl='https://capitainedabord.com/en/products/paul-shark-casquette-de-nylon-yachting',description='Кепка Yachting с вышитыми морскими флагами и изогнутым козырьком.',composition='Верх: 100% нейлон; подкладка: 87% полиэстер, 13% полиуретан',sizes=['1','2'])
]
cutouts={}
for p in products:
    im=cutout(refs/p['original']);cutouts[p['id']]=im
    bounds=(520,800) if p['category']=='Брюки' else (600,530) if p['category']=='Кепки' else (624,760)
    im=fitted(im,bounds);canvas=Image.new('RGBA',(720,900));canvas.alpha_composite(im,((720-im.width)//2,(900-im.height)//2))
    p['catalogPhoto']='/images/catalog/'+p['id']+'.webp';canvas.save(root/('public'+p['catalogPhoto']),quality=91,method=6)
    p['priceBasis']='Цена витрины FORME; не подтверждённая цена магазина-источника'
    if 'referenceInstagram' in p:p['match']='Похожая модель, не подтверждена как точная вещь из Instagram'
hoodie=Image.open(root/'public/images/catalog/packshot-37.webp').convert('RGBA');hoodie=hoodie.crop(hoodie.getchannel('A').getbbox())
for id,name,top,bottom,price,url,parts in [
 ('merano-set','Комплект Loro Piana Merano',hoodie,cutouts['merano-trousers'],23800,products[0]['sourceUrl'],['Худи Loro Piana Merano','Брюки Loro Piana Merano']),
 ('cd-icon-set','Подборка Dior CD Icon',cutouts['cd-icon-halfzip'],cutouts['cd-icon-trousers'],31800,products[2]['sourceUrl'],['Свитшот Dior CD Icon Half-Zip, графитовый','Брюки Dior CD Icon, серые'])]:
    canvas=Image.new('RGBA',(720,900))
    for im,bounds,y in [(top,(400,385),32),(bottom,(300,455),422)]:
        im=fitted(im,bounds);canvas.alpha_composite(im,((720-im.width)//2,y))
    path='/images/catalog/'+id+'.webp';canvas.save(root/('public'+path),quality=91,method=6)
    products.append(dict(id=id,name=name,model=name,category='Комплекты',color='Светло-серый' if id=='merano-set' else 'Графитовый / серый',hex='#b2b3ae' if id=='merano-set' else '#343436',price=price,sourceUrl=url,catalogPhoto=path,parts=parts,description='Сочетание двух отдельных вещей: '+', '.join(parts)+'.',match='Подборка из отдельных предметных фотографий; не заявлена как точный комплект из Instagram',priceBasis='Сумма цен отдельных вещей в витрине FORME'))
write('src/seasonProducts.js','export const seasonProducts = '+json.dumps([{k:v for k,v in p.items() if k!='original'} for p in products],ensure_ascii=False,indent=2)+';\n')
write('references/nov20/used-products.json',json.dumps(products,ensure_ascii=False,indent=2))

data=read('src/data.js').replace("import {packshotProducts}","import {seasonProducts} from './seasonProducts.js';\nimport {packshotProducts}",1)
data=data.replace('data.push(...packshotProducts);',"data.push(...packshotProducts.filter(p=>p.id!=='packshot-0'),...seasonProducts);")
write('src/data.js',data)
main=read('src/main.jsx')
main=main.replace('<Carousel look={look} onChange={L}/></div>', '<Carousel look={look} onChange={L}/><div className="look-purchase"><div><span className="small-label">Весь образ</span><span className="price">{money(outfit.price)}</span></div><button className="primary" onClick={()=>{add(outfit);M(\'cart\')}}>Купить образ<Icon kind="bag"/></button></div></div>')
main=main.replace('<section className="current-looks" aria-labelledby="current-title"><div className="section-heading"><div><h2 id="current-title">Актуальные образы</h2></div></div>','<section className="current-looks" aria-label="Фотографии коллекции">')
main=main.replace('</button><h3>{item.title}</h3></article>','</button></article>')
main='\n'.join(line for line in main.splitlines() if not line.startswith(' {inLook&&!modal&&!menu&&'))
main=main.replace(',[inLook,InLook]=useState(false)','')
main='\n'.join(line for line in main.splitlines() if 'const section=document.querySelector(\'.wardrobe\')' not in line)
write('src/main.jsx',main+'\n')
css=read('src/style.css')+'\n/* November collection: photographic hero and compact, in-flow purchase action. */\n'+'''
.hero-photos img{object-fit:cover;object-position:center 32%}
.hero:before{height:26%;min-height:160px;background:linear-gradient(to bottom,rgba(0,0,0,.88),rgba(0,0,0,.4) 45%,transparent)}
.hero:after{height:48%;background:linear-gradient(to top,rgba(0,0,0,.88),rgba(0,0,0,.48) 48%,transparent)}
.top-brands{padding-block:24px 20px}
.brand-grid{grid-template-columns:repeat(4,minmax(0,1fr));gap:12px 16px;max-width:760px;margin-top:16px}
.brand-mark img{max-width:100%;object-fit:contain}
.brand-mark img[src$="tommy.svg"]{max-width:70px;height:38px}
.current-looks{padding:18px 0 24px;border-top:1px solid rgba(0,0,0,.14)}
.current-looks-grid>article:nth-child(5) img{object-position:center}
.wardrobe{padding-bottom:28px}
.look-purchase{display:flex;align-items:center;justify-content:center;gap:24px;margin:16px auto 0;padding:0 8px;max-width:560px}
.look-purchase>div{display:flex;flex-direction:column;gap:6px}
.look-purchase .primary{width:auto;min-width:160px;min-height:44px;padding:10px 18px;gap:12px}
.look-details{margin-top:24px}
@media(min-width:651px){.top-brands{padding-block:28px 24px}.current-looks{padding-block:20px 28px}.look-purchase{gap:40px}.hero-photos img{object-position:center 36%}}
'''
write('src/style.css',css)
build=read('scripts/build.mjs').replace('{currentEditorials,featuredBrands}', '{currentEditorials,heroPhotos,featuredBrands}').replace('...currentEditorials.map','...heroPhotos.map(p=>p.image.slice(1)),...currentEditorials.map').replace(",'images/hero-01.webp','images/hero-02.webp','images/hero-03.webp'",'')
write('scripts/build.mjs',build)
check=read('scripts/check.mjs').replace('catalogData.length,51','catalogData.length,57').replace("p.category==='Кепки').length,6","p.category==='Кепки').length,8")
write('scripts/check.mjs',check)
print('Prepared 6 editorial originals, 7 products and 2 brand logos; interface updated.')

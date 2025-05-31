import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import random
import os
import re



def get_ntv_news(target_per_category=200):
    """
    NTV'den haber metinlerini ve kategorilerini çeken fonksiyon
    
    Args:
        target_per_category: Her kategoriden çekilecek hedef haber sayısı
    """
    # NTV kategorileri
    categories = {
        'dunya': 'https://www.ntv.com.tr/dunya',
        'ekonomi': 'https://www.ntv.com.tr/ekonomi',
        'spor': 'https://www.ntv.com.tr/spor',
        'egitim': 'https://www.ntv.com.tr/egitim',
        'sanat': 'https://www.ntv.com.tr/sanat',
        'yasam': 'https://www.ntv.com.tr/yasam',
        'teknoloji': 'https://www.ntv.com.tr/teknoloji',
        'saglik': 'https://www.ntv.com.tr/saglik'
    }
    
    news_data = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for category, url in categories.items():
        print(f"{category.capitalize()} kategorisinden haberler çekiliyor...")
        category_count = 0
        
        try:
            # Her istek arasında rastgele bekleme süresi
            time.sleep(random.uniform(1, 2))
            
            print(f"  - Kategori sayfası inceleniyor: {url}")
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Tüm linkleri bul
            all_links = soup.find_all('a', href=True)
            news_links = []
            
            # Haber linklerini filtrele
            for link in all_links:
                href = link.get('href', '')
                # NTV haber linklerini filtrele
                if href.startswith('/') and '/' in href[1:] and not href.startswith('/video') and not any(item.get('url') == 'https://www.ntv.com.tr' + href for item in news_data):
                    news_links.append('https://www.ntv.com.tr' + href)
            
            # Tekrarlanan linkleri kaldır
            news_links = list(set(news_links))
            print(f"  - {len(news_links)} adet haber linki bulundu.")
            
            # Haberleri çek
            for news_url in news_links:
                # Hedef sayıya ulaşıldıysa döngüyü kır
                if category_count >= target_per_category:
                    break
                    
                try:
                    # Her haber isteği arasında kısa bekleme
                    time.sleep(random.uniform(0.2, 0.5))
                    
                    print(f"  - Haber çekiliyor: {news_url}")
                    news_response = requests.get(news_url, headers=headers)
                    news_soup = BeautifulSoup(news_response.content, 'html.parser')
                    
                    # Haber başlığı - birden fazla seçici dene
                    title = None
                    
                    # Meta etiketlerinden başlığı bul (daha güvenilir)
                    meta_title = news_soup.find('meta', property='og:title')
                    if meta_title:
                        title = meta_title.get('content', '')
                    
                    # Meta etiketlerinde yoksa diğer seçicileri dene
                    if not title:
                        for selector in ['h1.category-detail-title', 'h1.title', 'h1', '.article-title']:
                            title_elem = news_soup.select_one(selector)
                            if title_elem:
                                title = title_elem.text.strip()
                                break
                    
                    if not title:
                        title = "Başlık bulunamadı"
                    
                    # Haber metni - daha kapsamlı içerik çekme stratejisi
                    content = ""
                    
                    # İçerik seçicilerini dene - önce ana içerik konteynerini bul
                    content_container = None
                    for selector in ['.category-detail-content', '.article-body', '.news-content', '.article-content', '.content', '.detail-content', '.detail-page-content']:
                        content_container = news_soup.select_one(selector)
                        if content_container:
                            break
                    
                    # İçerik konteynerı bulunduysa, tüm metin elemanlarını topla
                    if content_container:
                        # Önce paragrafları bul
                        paragraphs = content_container.find_all(['p', 'h2', 'h3', 'h4', 'li', 'blockquote'])
                        if paragraphs:
                            content = ' '.join([p.text.strip() for p in paragraphs])
                        
                        # Eğer paragraf bulunamadıysa, tüm metni al
                        if not content:
                            content = content_container.text.strip()
                    
                    # İçerik hala boşsa, meta açıklamasını dene
                    if not content:
                        meta_desc = news_soup.find('meta', property='og:description')
                        if meta_desc:
                            content = meta_desc.get('content', '')
                    
                    # İçerik hala bulunamadıysa
                    if not content:
                        content = "İçerik bulunamadı"
                    
                    # Başlık ve içerik bulunabildiyse ekle
                    if title != "Başlık bulunamadı" and content != "İçerik bulunamadı":
                        # Metin temizleme
                        content = re.sub(r'\s+', ' ', content).strip()
                        
                        news_data.append({
                            'category': category,
                            'title': title,
                            'content': content,
                            'url': news_url,
                            'source': 'ntv',
                            'date': datetime.now().strftime("%Y-%m-%d")
                        })
                        category_count += 1
                        print(f"  - '{title[:50]}...' haberi eklendi. ({category}: {category_count}/{target_per_category})")
                    else:
                        print(f"  ! Başlık veya içerik bulunamadı: {news_url}")
                        
                except Exception as e:
                    print(f"  ! Haber çekilirken hata oluştu: {str(e)}")
                    continue
            
            # Eğer ana sayfadan yeterli haber çekilemediyse, alt kategorileri kontrol et
            if category_count < target_per_category:
                print(f"  - Ana sayfadan {category_count} haber çekildi. Alt kategoriler kontrol ediliyor...")
                
                # Alt kategorileri bul
                subcategory_links = []
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    # Alt kategori linklerini filtrele
                    if href.startswith('/') and category in href and url != 'https://www.ntv.com.tr' + href and not any(href in s for s in subcategory_links):
                        subcategory_links.append('https://www.ntv.com.tr' + href)
                
                # Alt kategorilerden haber çek
                for sub_url in subcategory_links[:5]:  # En fazla 5 alt kategori
                    if category_count >= target_per_category:
                        break
                        
                    try:
                        print(f"  - Alt kategori inceleniyor: {sub_url}")
                        time.sleep(random.uniform(1, 2))
                        
                        sub_response = requests.get(sub_url, headers=headers)
                        sub_soup = BeautifulSoup(sub_response.content, 'html.parser')
                        
                        # Alt kategorideki haber linklerini bul
                        sub_news_links = []
                        for link in sub_soup.find_all('a', href=True):
                            href = link.get('href', '')
                            if href.startswith('/') and '/' in href[1:] and not href.startswith('/video') and not any(item.get('url') == 'https://www.ntv.com.tr' + href for item in news_data):
                                sub_news_links.append('https://www.ntv.com.tr' + href)
                        
                        sub_news_links = list(set(sub_news_links))
                        print(f"  - Alt kategoride {len(sub_news_links)} adet haber linki bulundu.")
                        
                        # Alt kategorideki haberleri çek
                        for news_url in sub_news_links:
                            if category_count >= target_per_category:
                                break
                                
                            try:
                                time.sleep(random.uniform(0.2, 0.5))
                                
                                news_response = requests.get(news_url, headers=headers)
                                news_soup = BeautifulSoup(news_response.content, 'html.parser')
                                
                                # Haber başlığı
                                title = None
                                meta_title = news_soup.find('meta', property='og:title')
                                if meta_title:
                                    title = meta_title.get('content', '')
                                
                                if not title:
                                    for selector in ['h1.category-detail-title', 'h1.title', 'h1', '.article-title']:
                                        title_elem = news_soup.select_one(selector)
                                        if title_elem:
                                            title = title_elem.text.strip()
                                            break
                                
                                if not title:
                                    title = "Başlık bulunamadı"
                                
                                # Haber metni - daha kapsamlı içerik çekme stratejisi
                                content = ""
                                
                                # İçerik seçicilerini dene - önce ana içerik konteynerini bul
                                content_container = None
                                for selector in ['.category-detail-content', '.article-body', '.news-content', '.article-content', '.content', '.detail-content', '.detail-page-content']:
                                    content_container = news_soup.select_one(selector)
                                    if content_container:
                                        break
                                
                                # İçerik konteynerı bulunduysa, tüm metin elemanlarını topla
                                if content_container:
                                    # Önce paragrafları bul
                                    paragraphs = content_container.find_all(['p', 'h2', 'h3', 'h4', 'li', 'blockquote'])
                                    if paragraphs:
                                        content = ' '.join([p.text.strip() for p in paragraphs])
                                    
                                    # Eğer paragraf bulunamadıysa, tüm metni al
                                    if not content:
                                        content = content_container.text.strip()
                                
                                # İçerik hala boşsa, meta açıklamasını dene
                                if not content:
                                    meta_desc = news_soup.find('meta', property='og:description')
                                    if meta_desc:
                                        content = meta_desc.get('content', '')
                                
                                # İçerik hala bulunamadıysa
                                if not content:
                                    content = "İçerik bulunamadı"
                                
                                # Başlık ve içerik bulunabildiyse ekle
                                if title != "Başlık bulunamadı" and content != "İçerik bulunamadı":
                                    content = re.sub(r'\s+', ' ', content).strip()
                                    
                                    news_data.append({
                                        'category': category,
                                        'title': title,
                                        'content': content,
                                        'url': news_url,
                                        'source': 'ntv',
                                        'date': datetime.now().strftime("%Y-%m-%d")
                                    })
                                    category_count += 1
                                    print(f"  - '{title[:50]}...' haberi eklendi. ({category}: {category_count}/{target_per_category})")
                                
                            except Exception as e:
                                print(f"  ! Alt kategorideki haber çekilirken hata oluştu: {str(e)}")
                                continue
                    
                    except Exception as e:
                        print(f"  ! Alt kategori sayfası çekilirken hata oluştu: {str(e)}")
                        continue
                
        except Exception as e:
            print(f"! {category} kategorisi çekilirken hata oluştu: {str(e)}")
            continue
            
        print(f"  = {category} kategorisinden toplam {category_count} haber çekildi.")
    
    return pd.DataFrame(news_data)

if __name__ == "__main__":
    # Data/raw klasörünü oluştur (yoksa)
    os.makedirs('data/raw', exist_ok=True)
    
    # Haber verilerini çek
    df = get_ntv_news(target_per_category=200)
    
    # Veri çekildi mi kontrol et
    if len(df) == 0:
        print("Hiç veri çekilemedi!")
    else:
        # CSV dosyasına kaydet
        output_file = 'data/raw/ntv_news_dataset.csv'
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"\nVeriler başarıyla {output_file} dosyasına kaydedildi!")
        print(f"Toplam {len(df)} haber çekildi.")
        print(f"Kategori dağılımı:\n{df['category'].value_counts()}") 
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
        'spor': 'https://www.ntv.com.tr/sporskor',
        'egitim': 'https://www.ntv.com.tr/egitim',
        'magazin': 'https://www.ntv.com.tr/n-life/magazin',
        'yasam': 'https://www.ntv.com.tr/yasam'
    }
    
    # Sayfa numaraları (daha fazla haber için)
    page_numbers = list(range(1, 21))  # 1'den 20'ye kadar sayfalar
    
    news_data = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for category, base_url in categories.items():
        print(f"{category.capitalize()} kategorisinden haberler çekiliyor...")
        category_count = 0
        
        for page in page_numbers:
            # Hedef sayıya ulaşıldıysa bu kategoriyi atla
            if category_count >= target_per_category:
                print(f"  - {category} kategorisi için hedef sayıya ({target_per_category}) ulaşıldı.")
                break
                
            # Sayfa URL'sini oluştur
            if page == 1:
                url = base_url
            else:
                url = f"{base_url}?page={page}"
                
            try:
                # Her istek arasında rastgele bekleme süresi
                time.sleep(random.uniform(1, 3))
                
                print(f"  - Sayfa {page} inceleniyor: {url}")
                response = requests.get(url, headers=headers)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Haber linklerini bul (NTV'ye özel CSS seçicileri)
                news_links = soup.select('a.card-text-link, a.card-img-link, .category-item a')
                
                if not news_links:
                    print(f"  ! Bu sayfada haber linki bulunamadı, farklı seçiciler deneniyor...")
                    # Alternatif seçiciler
                    news_links = soup.find_all('a', href=True)
                    # Sadece haber linklerini filtrele
                    news_links = [link for link in news_links if '/haber/' in link.get('href', '')]
                
                print(f"  - {len(news_links)} adet haber linki bulundu.")
                
                # Bu sayfada hiç link bulunamadıysa sonraki sayfaya geç
                if not news_links:
                    print("  ! Bu sayfada haber linki bulunamadı, sonraki sayfaya geçiliyor.")
                    continue
                
                for link in news_links:
                    # Hedef sayıya ulaşıldıysa döngüyü kır
                    if category_count >= target_per_category:
                        break
                        
                    news_url = link.get('href')
                    if news_url:
                        # Tam URL oluştur
                        if not news_url.startswith('http'):
                            news_url = 'https://www.ntv.com.tr' + news_url
                            
                        # Tekrar eden haberleri kontrol et
                        if any(item.get('url') == news_url for item in news_data):
                            continue
                            
                        try:
                            # Her haber isteği arasında rastgele bekleme
                            time.sleep(random.uniform(0.5, 1.5))
                            
                            news_response = requests.get(news_url, headers=headers)
                            news_soup = BeautifulSoup(news_response.content, 'html.parser')
                            
                            # Haber başlığı
                            title = news_soup.select_one('h1.category-detail-title, h1.title')
                            title = title.text.strip() if title else "Başlık bulunamadı"
                            
                            # Haber metni
                            content_parts = news_soup.select('div.category-detail-content p, article p')
                            content = ' '.join([p.text.strip() for p in content_parts]) if content_parts else "İçerik bulunamadı"
                            
                            # İçerik çok kısaysa meta açıklamasını kontrol et
                            if len(content) < 100:
                                meta_desc = news_soup.find('meta', property='og:description')
                                if meta_desc:
                                    content = meta_desc.get('content', content)
                            
                            # Metin temizleme
                            content = re.sub(r'\s+', ' ', content).strip()
                            
                            # Başlık ve içerik bulunabildiyse ekle
                            if title != "Başlık bulunamadı" and content != "İçerik bulunamadı":
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
                            
            except Exception as e:
                print(f"! {category} kategorisi, sayfa {page} çekilirken hata oluştu: {str(e)}")
                continue
                
        print(f"  = {category} kategorisinden toplam {category_count} haber çekildi.")
    
    return pd.DataFrame(news_data)

if __name__ == "__main__":
    # Data/raw klasörünü oluştur (yoksa)
    os.makedirs('data/raw', exist_ok=True)
    
    # Haber verilerini çek
    df = get_ntv_news(target_per_category=200)
    
    # CSV dosyasına kaydet
    if len(df) > 0:
        output_file = 'data/raw/ntv_news_dataset.csv'
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"\nVeriler başarıyla {output_file} dosyasına kaydedildi!")
        print(f"Toplam {len(df)} haber çekildi.")
        print(f"Kategori dağılımı:\n{df['category'].value_counts()}")
    else:
        print("Hiç veri çekilemedi!") 
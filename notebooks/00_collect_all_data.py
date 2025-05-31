import pandas as pd
import os
import time
from datetime import datetime
import importlib.util
import sys

def import_module_from_file(module_name, file_path):
    """Belirtilen dosya yolundan bir modül yükler"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def collect_all_data(target_per_category=200):
    """
    Tüm haber kaynaklarından veri çekip birleştiren fonksiyon
    
    Args:
        target_per_category: Her kategoriden çekilecek hedef haber sayısı
    """
    # Data/raw klasörünü oluştur (yoksa)
    os.makedirs('data/raw', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    
    print("=" * 50)
    print(f"VERİ TOPLAMA İŞLEMİ BAŞLADI: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    all_data = []
    
    # Modülleri dinamik olarak yükle
    cnn_module = import_module_from_file("cnn_scrapping", "notebooks/01_cnn_scrapping.py")
    ntv_module = import_module_from_file("ntv_scrapping", "notebooks/04_ntv_scrapping.py")
    
    # CNN Türk'ten veri çek
    print("\n1. CNN Türk'ten veriler çekiliyor...")
    cnn_df = cnn_module.get_cnn_news(target_per_category=target_per_category)
    if len(cnn_df) > 0:
        cnn_df.to_csv('data/raw/cnnturk_news_dataset.csv', index=False, encoding='utf-8')
        all_data.append(cnn_df)
        print(f"  - {len(cnn_df)} haber çekildi ve kaydedildi.")
    else:
        print("  ! CNN Türk'ten hiç veri çekilemedi.")
    
    # NTV'den veri çek
    print("\n2. NTV'den veriler çekiliyor...")
    ntv_df = ntv_module.get_ntv_news(target_per_category=target_per_category)
    if len(ntv_df) > 0:
        ntv_df.to_csv('data/raw/ntv_news_dataset.csv', index=False, encoding='utf-8')
        all_data.append(ntv_df)
        print(f"  - {len(ntv_df)} haber çekildi ve kaydedildi.")
    else:
        print("  ! NTV'den hiç veri çekilemedi.")
    
    # Tüm verileri birleştir
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        combined_df.to_csv('data/processed/all_news_dataset.csv', index=False, encoding='utf-8')
        
        print("\n" + "=" * 50)
        print(f"VERİ TOPLAMA İŞLEMİ TAMAMLANDI: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Toplam {len(combined_df)} haber çekildi.")
        print(f"Kaynak dağılımı:\n{combined_df['source'].value_counts()}")
        print(f"Kategori dağılımı:\n{combined_df['category'].value_counts()}")
        print("=" * 50)
        
        return combined_df
    else:
        print("\n" + "=" * 50)
        print("Hiçbir kaynaktan veri çekilemedi!")
        print("=" * 50)
        return pd.DataFrame()

if __name__ == "__main__":
    collect_all_data(target_per_category=200) 
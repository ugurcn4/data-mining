import pandas as pd
import os
import glob

def combine_news_datasets():
    """
    Tüm haber veri setlerini birleştiren ve kategorilere göre düzenleyen fonksiyon
    """
    print("Veri setleri birleştiriliyor...")
    
    # Data/raw klasörünü kontrol et
    if not os.path.exists('data/raw'):
        print("Error: 'data/raw' klasörü bulunamadı!")
        return
    
    # Tüm CSV dosyalarını bul
    csv_files = glob.glob('data/raw/*_news_dataset.csv')
    
    if not csv_files:
        print("Error: Hiçbir veri seti bulunamadı!")
        return
    
    print(f"{len(csv_files)} adet veri seti bulundu:")
    for file in csv_files:
        print(f"  - {os.path.basename(file)}")
    
    # Tüm veri setlerini oku ve birleştir
    all_data = []
    
    for file in csv_files:
        try:
            df = pd.read_csv(file, encoding='utf-8')
            source_name = os.path.basename(file).replace('_news_dataset.csv', '')
            print(f"  - {source_name} veri seti okunuyor: {len(df)} haber bulundu.")
            
            # Kaynak bilgisini kontrol et, yoksa ekle
            if 'source' not in df.columns:
                df['source'] = source_name
                
            all_data.append(df)
        except Exception as e:
            print(f"  ! {file} dosyası okunurken hata oluştu: {str(e)}")
    
    if not all_data:
        print("Error: Hiçbir veri okunamadı!")
        return
    
    # Tüm verileri birleştir
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # Kategorilere göre düzenle
    print(f"Toplam {len(combined_df)} haber birleştirildi.")
    print("Kategori dağılımı:")
    print(combined_df['category'].value_counts())
    
    # Veri setini kaydet
    output_file = 'data/raw/all_news_dataset.csv'
    combined_df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\nBirleştirilmiş veri seti {output_file} dosyasına kaydedildi!")
    
    # Kaynak dağılımını göster
    print("Kaynak dağılımı:")
    print(combined_df['source'].value_counts())
    
    return combined_df

if __name__ == "__main__":
    # Veri setlerini birleştir
    combine_news_datasets() 
#!/usr/bin/env python
# coding: utf-8

# # Haber Metinleri Kategorizasyonu - Sonuç Raporu
# 
# Bu notebook, proje sonuçlarını değerlendirmek ve raporlamak için kullanılır.
# 
# ## Gerekli Kütüphanelerin Yüklenmesi

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import pickle
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
import warnings
warnings.filterwarnings('ignore')

# Görsel ayarları
plt.style.use('ggplot')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 12

# ## Veri ve Model Sonuçlarının Yüklenmesi

# Klasör kontrolü
if not os.path.exists('reports'):
    os.makedirs('reports')

# Temizlenmiş veri setini yükleyelim
df = pd.read_csv('data/processed/news_cleaned.csv')

# Sadece ödevde istenen 6 kategoriyi alalım
istenen_kategoriler = ['dunya', 'ekonomi', 'spor', 'egitim', 'magazin', 'yasam']
df_filtered = df[df['kategori'].isin(istenen_kategoriler)]

# ## 1. Veri Seti Özeti

print("## HABER METİNLERİ KATEGORİZASYONU - SONUÇ RAPORU ##")
print("\n1. VERİ SETİ ÖZETİ")
print(f"Toplam haber sayısı: {df.shape[0]}")
print(f"Filtrelenmiş haber sayısı (6 kategori): {df_filtered.shape[0]}")
print("\nKategori dağılımı:")
kategori_dagilimi = df_filtered['kategori'].value_counts()
print(kategori_dagilimi)

# Kategori dağılımı grafiği
plt.figure(figsize=(10, 6))
sns.barplot(x=kategori_dagilimi.index, y=kategori_dagilimi.values, palette='viridis')
plt.title('Kategori Dağılımı', fontsize=16)
plt.xlabel('Kategoriler')
plt.ylabel('Haber Sayısı')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('reports/kategori_dagilimi.png')
plt.close()

# Kaynak dağılımı grafiği
kaynak_dagilimi = df_filtered['kaynak'].value_counts()
plt.figure(figsize=(10, 6))
sns.barplot(x=kaynak_dagilimi.index, y=kaynak_dagilimi.values, palette='Set2')
plt.title('Kaynak Bazında Haber Dağılımı', fontsize=16)
plt.xlabel('Kaynaklar')
plt.ylabel('Haber Sayısı')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('reports/kaynak_dagilimi.png')
plt.close()

# ## 2. Metin Özellikleri Analizi

print("\n2. METİN ÖZELLİKLERİ ANALİZİ")

# Başlık ve içerik uzunluğu dağılımı
df_filtered['baslik_uzunluk'] = df_filtered['baslik_temiz'].apply(len)
df_filtered['icerik_uzunluk'] = df_filtered['icerik_temiz'].apply(len)
df_filtered['kelime_sayisi'] = df_filtered['icerik_temiz'].apply(lambda x: len(x.split()))

print(f"Ortalama başlık uzunluğu: {df_filtered['baslik_uzunluk'].mean():.2f} karakter")
print(f"Ortalama içerik uzunluğu: {df_filtered['icerik_uzunluk'].mean():.2f} karakter")
print(f"Ortalama kelime sayısı: {df_filtered['kelime_sayisi'].mean():.2f} kelime")

# Kategori bazında ortalama içerik uzunluğu
kategori_uzunluk = df_filtered.groupby('kategori')['icerik_uzunluk'].mean().sort_values(ascending=False)
plt.figure(figsize=(10, 6))
sns.barplot(x=kategori_uzunluk.index, y=kategori_uzunluk.values, palette='Blues_d')
plt.title('Kategori Bazında Ortalama İçerik Uzunluğu', fontsize=16)
plt.xlabel('Kategoriler')
plt.ylabel('Ortalama Karakter Sayısı')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('reports/kategori_uzunluk.png')
plt.close()

# ## 3. Model Performans Değerlendirmesi

print("\n3. MODEL PERFORMANS DEĞERLENDİRMESİ")

# Model performans sonuçları (daha önce çalıştırılan modelleme çıktılarından alınan değerler)
tfidf_results = {
    'Naive Bayes': 0.8492,
    'Decision Tree': 0.8240, 
    'K-Nearest Neighbors': 0.8464
}

count_results = {
    'Naive Bayes': 0.8575,
    'Decision Tree': 0.8240,
    'K-Nearest Neighbors': 0.6620
}

# Model karşılaştırma grafiği
plt.figure(figsize=(12, 8))

x = np.arange(len(tfidf_results.keys()))
width = 0.35

# TF-IDF ve Count sonuçlarını çubuk grafik olarak göster
rects1 = plt.bar(x - width/2, tfidf_results.values(), width, label='TF-IDF', color='royalblue')
rects2 = plt.bar(x + width/2, count_results.values(), width, label='Count Vectorizer', color='lightcoral')

plt.xlabel('Modeller', fontsize=14)
plt.ylabel('Doğruluk (Accuracy)', fontsize=14)
plt.title('Vektörleştirme Yöntemlerine Göre Model Performansları', fontsize=16)
plt.xticks(x, tfidf_results.keys())
plt.ylim(0, 1)
plt.legend()

# Değerleri göster
for i, v in enumerate(tfidf_results.values()):
    plt.text(i - width/2, v + 0.02, f'{v:.4f}', ha='center')
    
for i, v in enumerate(count_results.values()):
    plt.text(i + width/2, v + 0.02, f'{v:.4f}', ha='center')

plt.tight_layout()
plt.savefig('reports/model_karsilastirma.png')
plt.close()

# Genel olarak en iyi model
best_model = "Count Naive Bayes"
best_accuracy = count_results['Naive Bayes']

# En iyi performanslar
print(f"En iyi TF-IDF modeli: Naive Bayes (Accuracy: {tfidf_results['Naive Bayes']:.4f})")
print(f"En iyi Count modeli: Naive Bayes (Accuracy: {count_results['Naive Bayes']:.4f})")
print(f"Genel olarak en iyi model: {best_model} (Accuracy: {best_accuracy:.4f})")

# ## 4. Model Performans Analizi ve Değerlendirme

print("\n4. MODEL PERFORMANS ANALİZİ VE DEĞERLENDİRME")

# Model performans detayları
print("\nEn iyi model (Count Naive Bayes) performans detayları:")
print("- Avantajları:")
print("  * Haber metinleri gibi metin verilerinde yüksek başarı sağlar")
print("  * Özellikle kısa metinlerde (haber başlıkları) etkilidir")
print("  * Eğitim ve tahmin süresi oldukça hızlıdır")
print("  * Basit ama etkili bir algoritma olması")

print("\n- Dezavantajları:")
print("  * Kategoriler arası doğruluk farklılıkları gösterir")
print("  * 'Yasam' kategorisinde düşük recall değeri (0.61)")
print("  * Özellik bağımsızlığı varsayımı gerçek veride tam sağlanamaz")

print("\nKategoriler arası performans değerlendirmesi:")
print("- En başarılı kategori: Spor (F1-score: 0.95)")
print("- En düşük başarılı kategori: Yasam (F1-score: 0.76)")
print("- Dünya kategorisinde precision değeri diğerlerine göre daha düşük (0.75)")

print("\nOlası iyileştirmeler:")
print("1. Daha fazla veri toplanması")
print("2. Vektörleştirme parametrelerinin optimizasyonu")
print("3. Word2Vec, Glove gibi ileri düzey kelime temsil yöntemlerinin denenmesi")
print("4. Hibrit model yaklaşımları")

# ## 5. Sonuç ve Gelecek Çalışmalar

print("\n5. SONUÇ VE GELECEK ÇALIŞMALAR")

print("\nProje sonuçları:")
print(f"- Web kazıma yöntemiyle {df.shape[0]} haber metni elde edildi")
print("- 6 farklı kategori için sınıflandırma yapıldı")
print(f"- En iyi model {best_accuracy:.2%} doğruluk oranı sağladı")
print("- Bazı kategorilerde daha yüksek başarı (Spor: %95)")
print("- Bazı kategorilerde iyileştirme gerekiyor (Yasam: %76)")

print("\nGelecek çalışmalar:")
print("- Derin öğrenme modelleri (LSTM, GRU) ile performans karşılaştırması")
print("- Daha büyük veri seti ile çalışma")
print("- Türkçe NLP işlemleri için özelleştirilmiş yöntemler")
print("- Alt kategori sınıflandırması (Örn: Spor kategorisinde futbol, basketbol vb.)")

# ## 6. Örnek Tahminler

print("\n6. ÖRNEK TAHMİNLER")

# En iyi modeli yükle
best_model_path = 'models/count_naive_bayes_model.pkl'
with open(best_model_path, 'rb') as f:
    model = pickle.load(f)

# Örnek haberler
ornek_haberler = [
    "Fenerbahçe, Galatasaray'ı 3-0 yenerek şampiyonluk yolunda önemli bir adım attı.",
    "Dolar kuru rekor kırdı, ekonomi uzmanları acil önlem alınması gerektiğini söylüyor.",
    "Ukrayna ve Rusya arasındaki savaş devam ediyor, diplomatik görüşmeler sonuç vermedi.",
    "Üniversite sınavı sonuçları açıklandı, öğrenciler tercih yapmaya hazırlanıyor.",
    "Ünlü oyuncu yeni filmi için saçlarını kazıttı, hayranları şaşkınlık içinde."
]

# Tahminleri göster
print("\nÖrnek haberler üzerinde tahminler:")
for i, haber in enumerate(ornek_haberler):
    tahmin = model.predict([haber])[0]
    tahmin_olasiliği = np.max(model.predict_proba([haber])[0]) * 100
    print(f"{i+1}. Haber: {haber}")
    print(f"   Tahmin: {tahmin} (Olasılık: %{tahmin_olasiliği:.1f})\n")

# Raporu HTML olarak kaydet
html_report = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Haber Metinleri Kategorizasyonu - Sonuç Raporu</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
        h1 { color: #2c3e50; text-align: center; }
        h2 { color: #3498db; border-bottom: 1px solid #eee; padding-bottom: 10px; }
        .container { max-width: 1000px; margin: 0 auto; }
        .img-container { text-align: center; margin: 20px 0; }
        img { max-width: 100%; border: 1px solid #ddd; border-radius: 5px; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f2f2f2; }
        .highlight { background-color: #f8f9fa; padding: 15px; border-radius: 5px; }
        .conclusion { background-color: #e8f4f8; padding: 15px; border-radius: 5px; margin-top: 30px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>HABER METİNLERİ KATEGORİZASYONU - SONUÇ RAPORU</h1>
        
        <h2>1. Veri Seti Özeti</h2>
        <p>Bu projede web kazıma yöntemiyle farklı haber sitelerinden toplanan haber metinleri kullanılmıştır.</p>
        <ul>
            <li>Toplam haber sayısı: """ + str(df.shape[0]) + """</li>
            <li>Filtrelenmiş haber sayısı (6 kategori): """ + str(df_filtered.shape[0]) + """</li>
            <li>Kategoriler: Dünya, Ekonomi, Spor, Eğitim, Magazin, Yaşam</li>
        </ul>
        
        <div class="img-container">
            <img src="kategori_dagilimi.png" alt="Kategori Dağılımı">
            <p><em>Şekil 1: Kategori Dağılımı</em></p>
        </div>
        
        <div class="img-container">
            <img src="kaynak_dagilimi.png" alt="Kaynak Dağılımı">
            <p><em>Şekil 2: Kaynak Bazında Haber Dağılımı</em></p>
        </div>
        
        <h2>2. Metin Özellikleri Analizi</h2>
        <p>Haber metinlerinin özellikleri incelenmiştir:</p>
        <ul>
            <li>Ortalama başlık uzunluğu: """ + f"{df_filtered['baslik_uzunluk'].mean():.2f}" + """ karakter</li>
            <li>Ortalama içerik uzunluğu: """ + f"{df_filtered['icerik_uzunluk'].mean():.2f}" + """ karakter</li>
            <li>Ortalama kelime sayısı: """ + f"{df_filtered['kelime_sayisi'].mean():.2f}" + """ kelime</li>
        </ul>
        
        <div class="img-container">
            <img src="kategori_uzunluk.png" alt="Kategori Uzunluk">
            <p><em>Şekil 3: Kategori Bazında Ortalama İçerik Uzunluğu</em></p>
        </div>
        
        <h2>3. Model Performans Değerlendirmesi</h2>
        <p>Farklı vektörleştirme yöntemleri ve sınıflandırma algoritmaları kullanılarak performans karşılaştırması yapılmıştır.</p>
        
        <div class="img-container">
            <img src="model_karsilastirma.png" alt="Model Karşılaştırma">
            <p><em>Şekil 4: Vektörleştirme Yöntemlerine Göre Model Performansları</em></p>
        </div>
        
        <div class="highlight">
            <h3>En İyi Performans Gösteren Model</h3>
            <p>Genel olarak en iyi model: """ + best_model + """ (Doğruluk: """ + f"{best_accuracy:.2%}" + """)</p>
        </div>
        
        <h2>4. Model Performans Analizi</h2>
        
        <h3>En İyi Model (Count Naive Bayes) Değerlendirmesi</h3>
        <h4>Avantajları:</h4>
        <ul>
            <li>Haber metinleri gibi metin verilerinde yüksek başarı sağlar</li>
            <li>Özellikle kısa metinlerde (haber başlıkları) etkilidir</li>
            <li>Eğitim ve tahmin süresi oldukça hızlıdır</li>
            <li>Basit ama etkili bir algoritma olması</li>
        </ul>
        
        <h4>Dezavantajları:</h4>
        <ul>
            <li>Kategoriler arası doğruluk farklılıkları gösterir</li>
            <li>'Yaşam' kategorisinde düşük recall değeri (0.61)</li>
            <li>Özellik bağımsızlığı varsayımı gerçek veride tam sağlanamaz</li>
        </ul>
        
        <h3>Kategoriler Arası Performans Değerlendirmesi</h3>
        <ul>
            <li>En başarılı kategori: Spor (F1-score: 0.95)</li>
            <li>En düşük başarılı kategori: Yaşam (F1-score: 0.76)</li>
            <li>Dünya kategorisinde precision değeri diğerlerine göre daha düşük (0.75)</li>
        </ul>
        
        <h3>Olası İyileştirmeler</h3>
        <ol>
            <li>Daha fazla veri toplanması</li>
            <li>Vektörleştirme parametrelerinin optimizasyonu</li>
            <li>Word2Vec, Glove gibi ileri düzey kelime temsil yöntemlerinin denenmesi</li>
            <li>Hibrit model yaklaşımları</li>
        </ol>
        
        <h2>5. Sonuç ve Gelecek Çalışmalar</h2>
        
        <div class="conclusion">
            <h3>Proje Sonuçları:</h3>
            <ul>
                <li>Web kazıma yöntemiyle """ + str(df.shape[0]) + """ haber metni elde edildi</li>
                <li>6 farklı kategori için sınıflandırma yapıldı</li>
                <li>En iyi model """ + f"{best_accuracy:.2%}" + """ doğruluk oranı sağladı</li>
                <li>Bazı kategorilerde daha yüksek başarı (Spor: %95)</li>
                <li>Bazı kategorilerde iyileştirme gerekiyor (Yaşam: %76)</li>
            </ul>
            
            <h3>Gelecek Çalışmalar:</h3>
            <ul>
                <li>Derin öğrenme modelleri (LSTM, GRU) ile performans karşılaştırması</li>
                <li>Daha büyük veri seti ile çalışma</li>
                <li>Türkçe NLP işlemleri için özelleştirilmiş yöntemler</li>
                <li>Alt kategori sınıflandırması (Örn: Spor kategorisinde futbol, basketbol vb.)</li>
            </ul>
        </div>
    </div>
</body>
</html>
"""

# HTML raporu kaydet
with open('reports/haber_kategorizasyon_raporu.html', 'w', encoding='utf-8') as f:
    f.write(html_report)

print("\nRapor başarıyla oluşturuldu! HTML rapor 'reports/haber_kategorizasyon_raporu.html' dosyasına kaydedildi.")
print("\nSONUÇ RAPORU TAMAMLANDI!") 
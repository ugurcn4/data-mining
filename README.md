# Türkçe Haber Metinleri Kategorizasyonu Projesi

Bu proje, çeşitli Türk haber kaynaklarından (CNN Türk, NTV, Habertürk ve Sabah) haber metinlerini çekerek kategorilere göre sınıflandıran ve analiz eden bir veri madenciliği çalışmasıdır.

## Proje İçeriği

Proje, aşağıdaki ana bileşenlerden oluşmaktadır:

1. **Veri Toplama**: Farklı haber kaynaklarından web scraping yöntemiyle haber metinlerinin toplanması
2. **Veri Ön İşleme**: Toplanan verilerin temizlenmesi, normalizasyonu ve analize hazırlanması
3. **Metin Vektörleştirme**: TF-IDF ve Count Vectorizer yöntemleriyle metin verilerinin sayısal vektörlere dönüştürülmesi
4. **Sınıflandırma Modellemesi**: Makine öğrenmesi algoritmaları kullanılarak haberlerin kategorilere göre sınıflandırılması
5. **Model Değerlendirmesi**: Farklı modellerin performanslarının karşılaştırılması ve en iyi modelin seçilmesi
6. **Sonuçların Raporlanması**: Elde edilen sonuçların görselleştirilmesi ve yorumlanması

## Veri Kaynakları

Proje kapsamında aşağıdaki haber kaynaklarından veri toplanmıştır:

| Kaynak | URL | Haber Sayısı |
|--------|-----|--------------|
| CNN Türk | https://www.cnnturk.com | 198 |
| NTV | https://www.ntv.com.tr | 605 |
| Habertürk | https://www.haberturk.com | 632 |
| Sabah | https://www.sabah.com.tr | 580 |
| **Toplam** | | **2015** |

## Haber Kategorileri

Toplanan haberler aşağıdaki kategorilere göre sınıflandırılmıştır:

| Kategori | Haber Sayısı | Yüzde |
|----------|--------------|-------|
| Spor | 505 | %25.1 |
| Ekonomi | 399 | %19.8 |
| Yaşam | 283 | %14.0 |
| Magazin | 256 | %12.7 |
| Dünya | 235 | %11.7 |
| Eğitim | 109 | %5.4 |
| Sağlık | 81 | %4.0 |
| Teknoloji | 75 | %3.7 |
| Sanat | 72 | %3.6 |
| **Toplam** | **2015** | **100%** |

## Proje Yapısı

```
veri_madenciligi/
│
├── data/
│   ├── raw/
│   │   ├── cnnturk_news_dataset.csv
│   │   ├── ntv_news_dataset.csv
│   │   ├── haberturk_news_dataset.csv
│   │   ├── sabah_news_dataset.csv
│   │   └── all_news_dataset.csv
│   └── processed/
│       └── news_cleaned.csv
│
├── models/
│   ├── tfidf_naive_bayes_model.pkl
│   ├── count_naive_bayes_model.pkl
│   ├── tfidf_decision_tree_model.pkl
│   └── count_decision_tree_model.pkl
│
├── notebooks/
│   ├── 01_cnn_scrapping.py
│   ├── 02_ntv_scrapping.py
│   ├── 03_haberturk_scrapping.py
│   ├── 04_sabah_scrapping.py
│   ├── 04_combine_datasets.py
│   ├── 05_veri_on_isleme.py
│   ├── 06_vektorlestirme_ve_modelleme.py
│   └── 07_sonuc_raporu.py
│
├── results/
│   ├── kategori_dagilimi.png
│   ├── kaynak_dagilimi.png
│   ├── uzunluk_dagilimi.png
│   ├── tfidf_model_karsilastirma.png
│   ├── count_model_karsilastirma.png
│   └── *_confusion_matrix.png
│
└── reports/
    └── haber_kategorizasyon_raporu.html
```

## Veri Toplama Süreci

Her bir haber kaynağı için ayrı bir Python betiği geliştirilmiştir. Bu betikler, BeautifulSoup ve Requests kütüphaneleri kullanılarak web scraping işlemi yapmaktadır. Veri toplama süreci şu adımları içerir:

1. Haber kategorilerine göre URL'lerin belirlenmesi
2. Her kategori sayfasından haber linklerinin çıkarılması
3. Her haber linkinden başlık ve içerik bilgilerinin çıkarılması
4. Verilerin CSV formatında kaydedilmesi

## Veri Ön İşleme

Veri ön işleme aşamasında aşağıdaki adımlar uygulanmıştır:

1. HTML etiketlerinin temizlenmesi
2. Noktalama işaretlerinin kaldırılması
3. Küçük harfe dönüştürme
4. Sayıların temizlenmesi
5. Türkçe stop words (gereksiz kelimeler) temizliği
6. Gereksiz boşlukların temizlenmesi

## Vektörleştirme ve Modelleme

Metin verilerini makine öğrenmesi algoritmaları ile işlenebilir hale getirmek için iki farklı vektörleştirme yöntemi kullanılmıştır:

1. **TF-IDF Vektörleştirme**
2. **Count Vektörleştirme**

Bu vektörleştirme yöntemleri ile üç farklı sınıflandırma algoritması denenmiştir:

1. **Naive Bayes**
2. **Decision Tree**
3. **K-Nearest Neighbors**

## Model Performans Sonuçları

| Model | TF-IDF Accuracy | Count Vectorizer Accuracy |
|-------|-----------------|---------------------------|
| Naive Bayes | 0.8492 | **0.8575** |
| Decision Tree | 0.8240 | 0.8240 |
| K-Nearest Neighbors | 0.8464 | 0.6620 |

En iyi performansı **Count Naive Bayes** modeli **%85.75** doğruluk oranı ile göstermiştir.

### Kategori Bazında Performans (Count Naive Bayes)

| Kategori | Precision | Recall | F1-Score |
|----------|-----------|--------|----------|
| Spor | 0.97 | 0.94 | 0.95 |
| Ekonomi | 0.85 | 0.91 | 0.88 |
| Dünya | 0.75 | 0.83 | 0.79 |
| Eğitim | 0.95 | 0.86 | 0.90 |
| Magazin | 0.69 | 0.90 | 0.78 |
| Yaşam | 1.00 | 0.61 | 0.76 |

## Kullanım

1. Veri toplama betiklerini çalıştırmak için:
```bash
python notebooks/00_collect_all_data.py
```

2. Veri ön işleme için:
```bash
python notebooks/05_veri_on_isleme.py
```

3. Vektörleştirme ve modelleme için:
```bash
python notebooks/06_vektorlestirme_ve_modelleme.py
```

4. Sonuç raporu oluşturmak için:
```bash
python notebooks/07_sonuc_raporu.py
```

## Gereksinimler

- Python 3+
- pandas
- numpy
- matplotlib
- seaborn
- nltk
- scikit-learn
- beautifulsoup4
- requests

## Sonuçlar ve Çıkarımlar

- Haber metinlerini kategorizasyon problemi yüksek başarıyla çözülebilmektedir (%85.75 doğruluk)
- Spor kategorisi en yüksek doğrulukla sınıflandırılabilen kategoridir (F1-score: 0.95)
- Yaşam kategorisi görece daha düşük başarıyla sınıflandırılabilmektedir (F1-score: 0.76)
- Farklı vektörleştirme yöntemleri farklı algoritmalarda farklı performans göstermektedir
- Naive Bayes, hem TF-IDF hem de Count Vectorizer ile en yüksek başarıyı sağlamıştır
- KNN algoritması, Count Vectorizer ile birlikte kullanıldığında performans düşüşü yaşamıştır

## Gelecek Çalışmalar

- Derin öğrenme modelleri (LSTM, GRU) ile performans karşılaştırması
- Daha büyük veri seti ile çalışma
- Türkçe NLP işlemleri için özelleştirilmiş yöntemler
- Alt kategori sınıflandırması (Örn: Spor kategorisinde futbol, basketbol vb.)

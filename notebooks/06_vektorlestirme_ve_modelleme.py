#!/usr/bin/env python
# coding: utf-8

# # Vektörleştirme ve Modelleme
# 
# Bu notebook, temizlenmiş haber verilerinin vektörleştirilmesi ve sınıflandırma modellerinin oluşturulması işlemlerini içerir.
#
# ## Gerekli Kütüphanelerin Yüklenmesi

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import pickle
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.pipeline import Pipeline
import warnings
warnings.filterwarnings('ignore')

# ## Temizlenmiş Veri Setinin Yüklenmesi

# Klasör kontrolü
if not os.path.exists('models'):
    os.makedirs('models')

# Temizlenmiş veri setini yükleyelim
df = pd.read_csv('data/processed/news_cleaned.csv')

# Veri seti hakkında genel bilgiler
print("Veri seti boyutu:", df.shape)
print("\nKategori dağılımı:")
print(df['kategori'].value_counts())

# Sadece ödevde istenen 6 kategoriyi alalım
istenen_kategoriler = ['dunya', 'ekonomi', 'spor', 'egitim', 'magazin', 'yasam']
df_filtered = df[df['kategori'].isin(istenen_kategoriler)]

print("\nFiltreleme sonrası kategori dağılımı:")
print(df_filtered['kategori'].value_counts())
print("\nFiltreleme sonrası veri boyutu:", df_filtered.shape)

# ## Veri Setinin Eğitim ve Test Olarak Ayrılması

# İçerik ve başlıkları birleştirme (opsiyonel)
df_filtered['metin'] = df_filtered['baslik_temiz'] + ' ' + df_filtered['icerik_temiz']

# Özellikler ve hedef değişkenin belirlenmesi
X = df_filtered['metin']  # Başlık ve içerik birleştirilmiş olarak
y = df_filtered['kategori']

# Veriyi eğitim ve test setlerine ayırma
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print("\nEğitim seti boyutu:", X_train.shape)
print("Test seti boyutu:", X_test.shape)

# ## Vektörleştirme

# TF-IDF Vektörleştirici
tfidf_vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2), min_df=5)

# Count Vektörleştirici (karşılaştırma için)
count_vectorizer = CountVectorizer(max_features=5000, ngram_range=(1, 2), min_df=5)

# ## Model Oluşturma ve Değerlendirme

def model_egit_degerlendir(model_ismi, model, vektorlestirici, X_train, X_test, y_train, y_test):
    """Modeli eğitir ve performansını değerlendirir"""
    
    # Pipeline oluşturma
    pipeline = Pipeline([
        ('vektorlestirici', vektorlestirici),
        ('model', model)
    ])
    
    # Modeli eğitme
    print(f"\n{model_ismi} eğitiliyor...")
    pipeline.fit(X_train, y_train)
    
    # Tahmin yapma
    y_pred = pipeline.predict(X_test)
    
    # Performans değerlendirme
    accuracy = accuracy_score(y_test, y_pred)
    print(f"{model_ismi} Doğruluk (Accuracy): {accuracy:.4f}")
    
    # Sınıflandırma raporu
    print("\nSınıflandırma Raporu:")
    class_report = classification_report(y_test, y_pred)
    print(class_report)
    
    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=pipeline.classes_, yticklabels=pipeline.classes_)
    plt.title(f'{model_ismi} Confusion Matrix')
    plt.ylabel('Gerçek Etiket')
    plt.xlabel('Tahmin Edilen Etiket')
    plt.tight_layout()
    plt.savefig(f'results/{model_ismi.lower().replace(" ", "_")}_confusion_matrix.png')
    plt.close()
    
    # Modeli kaydetme
    with open(f'models/{model_ismi.lower().replace(" ", "_")}_model.pkl', 'wb') as f:
        pickle.dump(pipeline, f)
    
    return pipeline, accuracy

# Modelleri tanımlama
models = {
    'Naive Bayes': MultinomialNB(),
    'Decision Tree': DecisionTreeClassifier(max_depth=100, random_state=42),
    'K-Nearest Neighbors': KNeighborsClassifier(n_neighbors=5)
}

# TF-IDF ile modelleri değerlendirme
print("\n## TF-IDF Vektörleştirici ile Modelleme ##")
tfidf_results = {}

for model_name, model in models.items():
    model_pipeline, accuracy = model_egit_degerlendir(
        f"TF-IDF {model_name}", 
        model, 
        tfidf_vectorizer, 
        X_train, X_test, y_train, y_test
    )
    tfidf_results[model_name] = accuracy

# Count Vectorizer ile modelleri değerlendirme
print("\n## Count Vektörleştirici ile Modelleme ##")
count_results = {}

for model_name, model in models.items():
    model_pipeline, accuracy = model_egit_degerlendir(
        f"Count {model_name}", 
        model, 
        count_vectorizer, 
        X_train, X_test, y_train, y_test
    )
    count_results[model_name] = accuracy

# ## Sonuçların Karşılaştırılması

# TF-IDF sonuçları
plt.figure(figsize=(12, 6))
plt.bar(tfidf_results.keys(), tfidf_results.values(), color='skyblue')
plt.title('TF-IDF Vektörleştirici ile Model Performansları')
plt.ylabel('Doğruluk (Accuracy)')
plt.ylim(0, 1)
for i, (model, acc) in enumerate(tfidf_results.items()):
    plt.text(i, acc + 0.02, f'{acc:.4f}', ha='center')
plt.savefig('results/tfidf_model_karsilastirma.png')
plt.close()

# Count Vectorizer sonuçları
plt.figure(figsize=(12, 6))
plt.bar(count_results.keys(), count_results.values(), color='lightgreen')
plt.title('Count Vektörleştirici ile Model Performansları')
plt.ylabel('Doğruluk (Accuracy)')
plt.ylim(0, 1)
for i, (model, acc) in enumerate(count_results.items()):
    plt.text(i, acc + 0.02, f'{acc:.4f}', ha='center')
plt.savefig('results/count_model_karsilastirma.png')
plt.close()

# ## En İyi Performans Gösteren Modeli Kullanarak Tahmin Örneği

# En iyi TF-IDF modeli
best_tfidf_model = max(tfidf_results.items(), key=lambda x: x[1])[0]
print(f"\nEn iyi TF-IDF modeli: {best_tfidf_model} (Accuracy: {tfidf_results[best_tfidf_model]:.4f})")

# En iyi Count modeli
best_count_model = max(count_results.items(), key=lambda x: x[1])[0]
print(f"En iyi Count modeli: {best_count_model} (Accuracy: {count_results[best_count_model]:.4f})")

# Genel olarak en iyi model
if tfidf_results[best_tfidf_model] >= count_results[best_count_model]:
    best_overall = f"TF-IDF {best_tfidf_model}"
    best_acc = tfidf_results[best_tfidf_model]
else:
    best_overall = f"Count {best_count_model}"
    best_acc = count_results[best_count_model]
    
print(f"\nGenel olarak en iyi model: {best_overall} (Accuracy: {best_acc:.4f})")

# En iyi modeli yükleyelim
best_model_path = f'models/{best_overall.lower().replace(" ", "_")}_model.pkl'
with open(best_model_path, 'rb') as f:
    best_model = pickle.load(f)

# Tahmin örneği
ornek_haberler = [
    "Fenerbahçe, Galatasaray'ı 3-0 yenerek şampiyonluk yolunda önemli bir adım attı.",
    "Dolar kuru rekor kırdı, ekonomi uzmanları acil önlem alınması gerektiğini söylüyor.",
    "Ukrayna ve Rusya arasındaki savaş devam ediyor, diplomatik görüşmeler sonuç vermedi.",
    "Üniversite sınavı sonuçları açıklandı, öğrenciler tercih yapmaya hazırlanıyor.",
    "Ünlü oyuncu yeni filmi için saçlarını kazıttı, hayranları şaşkınlık içinde."
]

print("\nÖrnek Haberler Üzerinde Tahmin:")
for i, haber in enumerate(ornek_haberler):
    tahmin = best_model.predict([haber])[0]
    print(f"{i+1}. Haber: {haber[:50]}...")
    print(f"   Tahmin Edilen Kategori: {tahmin}\n")

print("\nVektörleştirme ve modelleme tamamlandı!") 
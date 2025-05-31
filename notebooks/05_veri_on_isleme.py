#!/usr/bin/env python
# coding: utf-8

# # Veri Ön İşleme
# 
# Bu notebook, toplanan ham haber verilerinin temizlenmesi ve işlenmesi işlemlerini içerir.
# 
# ## Gerekli Kütüphanelerin Yüklenmesi

import pandas as pd
import numpy as np
import re
import string
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import os
import sys
import warnings
warnings.filterwarnings('ignore')

# Türkçe NLP işlemleri için gerekli kütüphaneler
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer

# NLTK kaynaklarını indir
nltk.download('punkt')
nltk.download('stopwords')

# ## Veri Setinin Yüklenmesi

# Veri klasörü kontrolü
if not os.path.exists('data/processed'):
    os.makedirs('data/processed')

# Tüm haber veri setini yükleyelim
df = pd.read_csv('data/raw/all_news_dataset.csv')

# Sütun isimlerini Türkçeye çevirme
df = df.rename(columns={
    'category': 'kategori',
    'title': 'baslik',
    'content': 'icerik',
    'url': 'url',
    'source': 'kaynak',
    'date': 'tarih'
})

# Veri seti hakkında genel bilgiler
print("Veri seti boyutu:", df.shape)
print("\nVeri seti sütunları:", df.columns.tolist())
print("\nKategori dağılımı:")
print(df['kategori'].value_counts())
print("\nKaynak dağılımı:")
print(df['kaynak'].value_counts())

# Eksik verilerin kontrolü
print("\nEksik veriler:")
print(df.isnull().sum())

# ## Veri Temizleme Fonksiyonları

def html_tag_temizle(metin):
    """HTML etiketlerini metinden temizler"""
    if isinstance(metin, str):
        temiz_metin = re.sub('<.*?>', ' ', metin)
        return temiz_metin
    return metin

def noktalama_temizle(metin):
    """Noktalama işaretlerini metinden temizler"""
    if isinstance(metin, str):
        translator = str.maketrans('', '', string.punctuation)
        return metin.translate(translator)
    return metin

def rakam_temizle(metin):
    """Sayıları metinden temizler"""
    if isinstance(metin, str):
        return re.sub(r'\d+', '', metin)
    return metin

def stopwords_temizle(metin):
    """Türkçe stop words kelimelerini metinden temizler"""
    if isinstance(metin, str):
        stop_words = set(stopwords.words('turkish'))
        kelimeler = word_tokenize(metin.lower(), language='turkish')
        filtered_kelimeler = [kelime for kelime in kelimeler if kelime.lower() not in stop_words]
        return ' '.join(filtered_kelimeler)
    return metin

def stemming_uygula(metin):
    """Türkçe kök bulma işlemini uygular"""
    if isinstance(metin, str):
        stemmer = SnowballStemmer('turkish')
        kelimeler = word_tokenize(metin.lower(), language='turkish')
        stemmed_kelimeler = [stemmer.stem(kelime) for kelime in kelimeler]
        return ' '.join(stemmed_kelimeler)
    return metin

def metin_temizle(metin):
    """Tüm temizleme işlemlerini sırayla uygular"""
    if isinstance(metin, str):
        metin = html_tag_temizle(metin)
        metin = noktalama_temizle(metin)
        metin = rakam_temizle(metin)
        metin = metin.lower()  # Küçük harfe dönüştürme
        metin = stopwords_temizle(metin)
        # stemming_uygula fonksiyonu isteğe bağlı olarak kullanılabilir
        # metin = stemming_uygula(metin)
        # Gereksiz boşlukları temizle
        metin = re.sub(r'\s+', ' ', metin).strip()
        return metin
    return metin

# ## Veri Temizleme İşlemi

print("\nVeri temizleme işlemi başlatılıyor...")

# Veri temizleme öncesi örnek göster
print("\nTemizleme öncesi örnek haber:")
ornek_index = df.sample(1).index[0]
print(f"Başlık: {df.loc[ornek_index, 'baslik']}")
print(f"İçerik (ilk 300 karakter): {str(df.loc[ornek_index, 'icerik'])[:300]}...")

# Başlık ve içerik sütunlarına temizleme işlemi uygula
tqdm.pandas(desc="Başlıklar temizleniyor")
df['baslik_temiz'] = df['baslik'].progress_apply(metin_temizle)

tqdm.pandas(desc="İçerikler temizleniyor")
df['icerik_temiz'] = df['icerik'].progress_apply(metin_temizle)

# Veri temizleme sonrası örnek göster
print("\nTemizleme sonrası örnek haber:")
print(f"Temiz Başlık: {df.loc[ornek_index, 'baslik_temiz']}")
print(f"Temiz İçerik (ilk 300 karakter): {str(df.loc[ornek_index, 'icerik_temiz'])[:300]}...")

# Eksik verilerin kontrolü ve temizlenmesi
print("\nTemizlik sonrası eksik veriler:")
print(df.isnull().sum())

# Boş başlık veya içeriği olan satırları filtreleme
df_filtered = df.dropna(subset=['baslik_temiz', 'icerik_temiz'])
df_filtered = df_filtered[df_filtered['baslik_temiz'] != '']
df_filtered = df_filtered[df_filtered['icerik_temiz'] != '']

print(f"\nFiltreleme sonrası kalan veri sayısı: {df_filtered.shape[0]} (Önceki: {df.shape[0]})")

# ## Veri Seti İstatistikleri

# Temizlenmiş veri setindeki kategorilerin dağılımı
plt.figure(figsize=(12, 6))
sns.countplot(y='kategori', data=df_filtered, order=df_filtered['kategori'].value_counts().index)
plt.title('Kategorilere Göre Haber Dağılımı')
plt.tight_layout()
plt.savefig('results/kategori_dagilimi.png')
plt.close()

# Kaynaklara göre dağılım
plt.figure(figsize=(12, 6))
sns.countplot(y='kaynak', data=df_filtered, order=df_filtered['kaynak'].value_counts().index)
plt.title('Kaynaklara Göre Haber Dağılımı')
plt.tight_layout()
plt.savefig('results/kaynak_dagilimi.png')
plt.close()

# Haber başlıklarının uzunluk dağılımı
df_filtered['baslik_uzunluk'] = df_filtered['baslik_temiz'].apply(len)
df_filtered['icerik_uzunluk'] = df_filtered['icerik_temiz'].apply(len)

plt.figure(figsize=(14, 6))
plt.subplot(1, 2, 1)
sns.histplot(df_filtered['baslik_uzunluk'], kde=True, bins=30)
plt.title('Haber Başlıklarının Uzunluk Dağılımı')
plt.xlabel('Karakter Sayısı')

plt.subplot(1, 2, 2)
sns.histplot(df_filtered['icerik_uzunluk'], kde=True, bins=30)
plt.title('Haber İçeriklerinin Uzunluk Dağılımı')
plt.xlabel('Karakter Sayısı')

plt.tight_layout()
plt.savefig('results/uzunluk_dagilimi.png')
plt.close()

# ## Temizlenmiş Veri Setini Kaydetme

# Temiz veri setini kaydet
df_filtered.to_csv('data/processed/news_cleaned.csv', index=False)
print("\nTemizlenmiş veri seti kaydedildi: 'data/processed/news_cleaned.csv'")

# Özet istatistikler
print("\nÖzet İstatistikler:")
print(f"Toplam haber sayısı: {df_filtered.shape[0]}")
print(f"Kategori sayısı: {df_filtered['kategori'].nunique()}")
print(f"Kaynak sayısı: {df_filtered['kaynak'].nunique()}")
print("\nKategori bazında haber sayıları:")
print(df_filtered['kategori'].value_counts())

print("\nVeri ön işleme tamamlandı!") 
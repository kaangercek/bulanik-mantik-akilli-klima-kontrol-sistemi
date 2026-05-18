# Bulanık Mantık Tabanlı Akıllı Klima Kontrol Sistemi

Bu proje, bulanık mantık dersi dönem ödevi için geliştirilmiş bir akıllı klima kontrol sistemidir. Sistem, ortam sıcaklığı, nem ve oda büyüklüğü değerlerini giriş olarak alır; Mamdani tipi bulanık çıkarım ve centroid durulaştırma ile uygun fan hızını üretir.

## Proje Özeti

- Gerçek dünya problemi: Ortam konforunun yalnızca sıcaklığa değil, nem ve oda büyüklüğüne de bağlı olması
- Giriş değişkenleri: `Sıcaklık`, `Nem`, `Oda Büyüklüğü`
- Çıkış değişkeni: `Fan Hızı`
- Kural tabanı: 27 adet `IF-THEN` kuralı
- Arayüz: `Streamlit`
- Sayısal hesaplama ve çizimler: `NumPy`, `Matplotlib`

## Neden Bulanık Mantık?

Klima kontrolü kesin sınırlar yerine sözel ve insan benzeri kararlar gerektirir. Örneğin `sıcaklık biraz yüksek`, `nem orta seviyede`, `oda büyük` gibi durumlar klasik eşik tabanlı yöntemlerle kaba biçimde temsil edilirken, bulanık mantık bu geçişleri daha doğal biçimde yönetebilir.

## Kullanılan Yöntem

Sistem aşağıdaki adımları içerir:

1. Giriş değerleri üyelik fonksiyonları ile bulanıklaştırılır.
2. Mamdani çıkarım mekanizması ile kurallar aktive edilir.
3. Her kuralın çıktısı `min` yöntemi ile kesilir.
4. Tüm kural çıktıları `max` yöntemi ile birleştirilir.
5. Sonuç, `centroid` durulaştırma ile tek bir fan hızı değerine dönüştürülür.

## Kurulum

```bash
python -m pip install -r requirements.txt
```

## Çalıştırma

```bash
streamlit run app.py
```

Arayüzde:

- Giriş değerleri slider ve sayısal kutu ile değiştirilebilir.
- Üyelik fonksiyonları grafik üzerinde gösterilir.
- Aktif kurallar listelenir.
- Durulaştırılmış fan hızı sayısal ve grafiksel biçimde sunulur.
- Hazır test senaryoları karşılaştırılabilir.

## Dosya Yapısı

```text
.
|-- Bulanik_Mantik_Akilli_Klima_Kontrol_Sistemi_Raporu.docx
|-- app.py
|-- README.md
|-- REPORT.md
|-- requirements.txt
|-- scripts
|   `-- generate_word_report.py
`-- src
    |-- __init__.py
    `-- fuzzy_climate_controller.py
```



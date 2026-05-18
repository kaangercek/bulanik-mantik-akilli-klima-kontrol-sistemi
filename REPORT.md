# Bulanık Mantık Tabanlı Akıllı Klima Kontrol Sistemi

## 1. Giriş ve Problem Tanımı

Geleneksel klimalar çoğu zaman yalnızca hedef sıcaklığa göre çalışır. Ancak kullanıcı konforu yalnızca sıcaklığa bağlı değildir. Nem oranı ve oda büyüklüğü de ortamın nasıl hissedildiğini doğrudan etkiler. Bu nedenle aynı sıcaklık değeri farklı koşullarda farklı fan hızı gerektirebilir.

Bu projede amaç, sıcaklık, nem ve oda büyüklüğünü birlikte değerlendirerek klima fan hızını bulanık mantık ile belirleyen bir kontrolcü geliştirmektir.

## 2. Gerçek Dünya Problemi

### 2.1 Problem Tanımı

Bir odadaki konfor düzeyini sağlayacak klima fan hızını belirlemek istiyoruz. Problemde kesin sınırlar yerine insan benzeri sözel değerlendirmeler vardır:

- Sıcaklık düşük, konforlu veya yüksek olabilir.
- Nem kuru, normal veya nemli olabilir.
- Oda küçük, orta veya büyük olabilir.

Bu nedenle problem bulanık mantık yaklaşımına uygundur.

### 2.2 Giriş ve Çıkış Değişkenleri

Giriş değişkenleri:

- Sıcaklık (`16 - 36 °C`)
- Nem (`20 - 90 %`)
- Oda Büyüklüğü (`10 - 60 m²`)

Çıkış değişkeni:

- Fan Hızı (`0 - 100 %`)

### 2.3 Bulanık Mantığın Uygunluğu

Bulanık mantık bu problem için uygundur çünkü:

- Ortam konforu kesin sınırlarla ifade edilemez.
- İnsan uzman bilgisi `IF-THEN` kuralları ile kolayca modele dönüştürülebilir.
- Girişler arasında yumuşak geçişler tanımlanabilir.
- Çıktı daha doğal ve kararlı biçimde elde edilir.

## 3. Sistem Tasarımı

### 3.1 Dilsel Değişkenler

Sıcaklık:

- Düşük
- Konforlu
- Yüksek

Nem:

- Kuru
- Normal
- Nemli

Oda Büyüklüğü:

- Küçük
- Orta
- Büyük

Fan Hızı:

- Çok Düşük
- Düşük
- Orta
- Yüksek
- Çok Yüksek

### 3.2 Üyelik Fonksiyonları

Projede üçgensel ve yamuksal üyelik fonksiyonları kullanılmıştır.

Sıcaklık için:

- Düşük: yamuksal
- Konforlu: üçgensel
- Yüksek: yamuksal

Nem için:

- Kuru: yamuksal
- Normal: üçgensel
- Nemli: yamuksal

Oda büyüklüğü için:

- Küçük: yamuksal
- Orta: üçgensel
- Büyük: yamuksal

Fan hızı için:

- Çok Düşük: yamuksal
- Düşük: üçgensel
- Orta: üçgensel
- Yüksek: üçgensel
- Çok Yüksek: yamuksal

### 3.3 Kural Tabanı

Sistemde toplam 27 adet kural kullanılmıştır. Bu sayı, ödev koşulundaki minimum 15 kural şartının üzerindedir.

| No | Sıcaklık | Nem | Oda Büyüklüğü | Fan Hızı |
|---|---|---|---|---|
| 1 | Düşük | Kuru | Küçük | Çok Düşük |
| 2 | Düşük | Kuru | Orta | Düşük |
| 3 | Düşük | Kuru | Büyük | Düşük |
| 4 | Düşük | Normal | Küçük | Düşük |
| 5 | Düşük | Normal | Orta | Düşük |
| 6 | Düşük | Normal | Büyük | Orta |
| 7 | Düşük | Nemli | Küçük | Düşük |
| 8 | Düşük | Nemli | Orta | Orta |
| 9 | Düşük | Nemli | Büyük | Orta |
| 10 | Konforlu | Kuru | Küçük | Düşük |
| 11 | Konforlu | Kuru | Orta | Orta |
| 12 | Konforlu | Kuru | Büyük | Orta |
| 13 | Konforlu | Normal | Küçük | Orta |
| 14 | Konforlu | Normal | Orta | Orta |
| 15 | Konforlu | Normal | Büyük | Yüksek |
| 16 | Konforlu | Nemli | Küçük | Orta |
| 17 | Konforlu | Nemli | Orta | Yüksek |
| 18 | Konforlu | Nemli | Büyük | Yüksek |
| 19 | Yüksek | Kuru | Küçük | Orta |
| 20 | Yüksek | Kuru | Orta | Yüksek |
| 21 | Yüksek | Kuru | Büyük | Yüksek |
| 22 | Yüksek | Normal | Küçük | Yüksek |
| 23 | Yüksek | Normal | Orta | Yüksek |
| 24 | Yüksek | Normal | Büyük | Çok Yüksek |
| 25 | Yüksek | Nemli | Küçük | Yüksek |
| 26 | Yüksek | Nemli | Orta | Çok Yüksek |
| 27 | Yüksek | Nemli | Büyük | Çok Yüksek |

### 3.4 Çıkarım Motoru

Projede Mamdani tipi bulanık çıkarım kullanılmıştır.

- `AND` işlemi için `min`
- Kural çıktılarının birleştirilmesi için `max`

Her kuralın aktivasyon seviyesi, ilgili giriş üyelik derecelerinin minimumu alınarak hesaplanır.

### 3.5 Durulaştırma

Durulaştırma için ağırlık merkezi (`centroid`) yöntemi kullanılmıştır.

Bu yöntem, birleştirilmiş çıktı kümesinin alan merkezini hesaplayarak tek bir sayısal fan hızı değeri üretir.

## 4. Python Uygulaması

Proje, `Streamlit` tabanlı bir arayüz ile geliştirilmiştir.

Arayüz özellikleri:

- Giriş değerlerini slider ve sayısal kutu ile değiştirme
- Hesapla butonu ile anlık sonuç üretme
- Üyelik fonksiyonlarını grafik olarak gösterme
- Aktif kuralları listeleme
- Kural aktivasyonlarını grafik olarak sunma
- Durulaştırılmış çıktıyı hem sayısal hem grafiksel gösterme
- Farklı senaryoları tablo ve grafik olarak karşılaştırma

## 5. Test Sonuçları ve Analiz

Sistemde örnek test senaryoları tanımlanmıştır. Bu senaryolar arayüz içinde tablo ve grafik olarak gösterilmektedir.

| Senaryo | Sıcaklık (°C) | Nem (%) | Oda Büyüklüğü (m²) | Fan Hızı (%) | Baskın Çıkış |
|---|---:|---:|---:|---:|---|
| Serin ve kuru küçük oda | 18 | 32 | 16 | 9.63 | Çok Düşük |
| Konforlu orta oda | 24 | 52 | 32 | 50.00 | Orta |
| Konforlu ama nemli büyük oda | 25 | 74 | 52 | 70.00 | Yüksek |
| Sıcak ve kuru orta oda | 31 | 38 | 34 | 70.00 | Yüksek |
| Sıcak ve nemli büyük oda | 34 | 84 | 58 | 90.71 | Çok Yüksek |
| Serin ama nemli büyük oda | 20 | 78 | 55 | 50.00 | Orta |

Analiz:

- Serin ve kuru küçük odada fan hızı yaklaşık `%9.63` ile çok düşük çıkmıştır. Bu sonuç enerji tasarrufu açısından uygundur.
- Konforlu sıcaklıkta ve orta büyüklükte odada sistem `%50` seviyesinde orta fan hızı önermiştir.
- Nem yükseldiğinde, sıcaklık çok artmasa bile fan hızının yükseldiği görülmektedir.
- En yüksek sonuç, beklendiği gibi sıcak ve nemli büyük odada elde edilmiştir.
- Oda büyüklüğü arttıkça aynı sıcaklık sınıfında daha yüksek fan çıktısı oluşma eğilimi vardır.

Bu sonuçlar, gerçek hayattaki beklentiler ile uyumludur.

## 6. Güçlü ve Zayıf Yönler

### Güçlü Yönler

- İnsan benzeri sözel karar mantığı sunar.
- Keskin eşiklere göre daha yumuşak sonuç verir.
- Görselleştirme sayesinde karar süreci açıklanabilir durumdadır.
- Kural tabanı kolayca genişletilebilir.

### Zayıf Yönler

- Kural tabanı uzman bilgisine bağlıdır.
- Üyelik fonksiyonlarının seçimi sonuçları etkiler.
- Çok sayıda giriş değişkeninde kural sayısı hızla artar.

## 7. Güncel Yaklaşımlar ile Kıyaslama

Klasik kontrol yöntemleri sabit eşiklerle çalıştığı için konfor algısını tam temsil edemez. Makine öğrenmesi tabanlı yöntemler veri varsa güçlü sonuçlar verebilir; ancak eğitim verisi, model açıklanabilirliği ve hesaplama maliyeti gibi ek gereksinimler doğurur.

Bulanık mantık ise:

- Az veri ile kurulabilir
- Uzman bilgisine dayanır
- Açıklanabilir yapıdadır
- Eğitim gerektirmeden uygulanabilir

Bu nedenle eğitim amaçlı ve açıklanabilir kontrol problemleri için oldukça uygundur.

## 8. Sonuç ve Değerlendirme

Bu projede, sıcaklık, nem ve oda büyüklüğüne bağlı olarak klima fan hızını belirleyen bulanık mantık tabanlı bir kontrol sistemi geliştirilmiştir. Sistem, girişleri bulanıklaştırmakta, kural tabanı ile çıkarım yapmakta ve centroid yöntemi ile sayısal çıktı üretmektedir.

Geliştirilen Python arayüzü sayesinde kullanıcı, giriş değerlerini manuel olarak değiştirip sistemin verdiği sonucu anlık biçimde inceleyebilmektedir. Bu yönüyle proje hem teorik hem uygulamalı olarak dönem ödevi gereksinimlerini karşılamaktadır.

## 9. Kaynakça

1. Lotfi A. Zadeh, "Fuzzy Sets", Information and Control, 1965.
2. Timothy J. Ross, *Fuzzy Logic with Engineering Applications*.
3. Streamlit Documentation.
4. NumPy Documentation.
5. Matplotlib Documentation.

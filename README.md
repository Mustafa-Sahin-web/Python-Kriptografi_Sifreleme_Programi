🛡️ Mahşer-V19: LSB Steganografi & Kriptografi Paneli
Bu proje, gizli mesajları bir görselin (PNG) piksellerine en gelişmiş şifreleme yöntemlerini kullanarak gömen ve geri çıkaran yüksek güvenlikli bir steganografi aracıdır. Sadece veriyi saklamakla kalmaz, aynı zamanda askeri düzeyde şifreleme protokolleriyle veriyi erişilmez kılar.

🚀 Öne Çıkan Özellikler
Çift Katmanlı Güvenlik: Veri hem şifrelenir hem de görselin içinde saklanır (Security by Obscurity + Strong Encryption).

Gelişmiş Kripto Motoru:

AES-256-GCM: Kimlik doğrulamalı ve yüksek hızlı simetrik şifreleme.

Argon2id: Kaba kuvvet (brute-force) saldırılarına karşı dirençli modern anahtar türetme fonksiyonu.

HKDF (SHA256): Anahtar çeşitlendirme ve güçlendirme.

Dinamik LSB (Least Significant Bit): Mesaj piksellere sırayla değil, bir anahtar yardımıyla rastgele (shuffled) dağıtılır. Bu sayede görsel analiz araçlarıyla verinin tespiti imkansızlaşır.

Modern GUI: Karanlık mod temalı, kullanımı kolay ve şık bir kullanıcı arayüzü.

Crash Guard: Beklenmedik hataları yakalayan ve sistemi ayakta tutan hata yönetim mekanizması.

🛠️ Teknik Mimari
Programın veri işleme akışı şu şekildedir:

Parola Güçlendirme: Kullanıcı parolası Argon2id ve rastgele bir Salt ile işlenir.

Anahtar Türetme: Türetilen anahtar HKDF (Ultra Şifreleme info etiketiyle) üzerinden geçirilerek AES ve Steganografi anahtarlarına bölünür.

Şifreleme: Mesaj AES-256-GCM ile şifrelenir (Nonce/IV dahil).

Gizleme: Şifreli veri, görselin piksellerindeki en önemsiz bitlere (LSB), steganografi anahtarıyla karıştırılmış bir sırada yerleştirilir.

📦 Kurulum
Projenin çalışması için Python 3.x ve aşağıdaki kütüphaneler gereklidir:

Bash
pip install pillow cryptography argon2-cffi
🕹️ Kullanım
Görsel Seç: Şifreleme yapılacak bir .png dosyası yükleyin.

Mesajı Yaz: Gizlemek istediğiniz stratejik veriyi girin.

Parola Belirle: Güçlü bir güvenlik anahtarı oluşturun.

Mühürle: "MÜHÜRLEDİ" ibaresini görene kadar bekleyin. Şifreli görsel İndirilenler klasörüne kaydedilecektir.

Deşifre: Şifreli görseli seçip aynı parolayı girerek "DEŞİFRE" butonuna basın.

⚠️ Önemli Notlar
Kayıpsız Format: Steganografi işlemi için sadece .png formatı desteklenir. .jpg gibi kayıplı formatlar veriyi bozar.

Kapasite: Görselin çözünürlüğü ne kadar yüksekse, içine gömebileceğiniz veri miktarı o kadar artar.

Versiyon Uyumu: HKDF içindeki info parametresi (örn: "Ultra Şifreleme") değiştirilirse, eski kodla mühürlenen dosyalar yeni kodla açılamaz.

⚖️ Yasal Uyarı
Bu yazılım eğitim ve kişisel veri güvenliği araştırmaları için geliştirilmiştir. Yazılımın kötüye kullanımından geliştirici sorumlu tutulamaz.

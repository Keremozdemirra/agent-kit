---
name: "hafiza-guncelle"
description: "Oturumda öğrenilenleri kalıcı hafızaya işler — yeni tercihler, proje bilgileri, kısaltmalar, kararlar. \"Bunu hatırla\", \"hafızaya ekle\", \"bunu not al\", \"bir daha sormana gerek kalmasın\" dendiğinde veya uzun bir oturumun sonunda kullan. Also triggers on \"remember this\", \"add this to memory\", \"save this so I don't have to repeat it\", \"note that down for next time\". Tek seferlik görev detayı, geçici durum veya şifre ve API anahtarı gibi hassas veri için kullanma."
---

# Hafıza Güncelleme

Amaç: aynı bilgiyi ikinci kez anlatmak zorunda kalmamak.

## Ne girer, ne girmez

**Girer** — tekrar tekrar geçerli olacak şeyler:
- Kalıcı tercihler ("raporları hep PDF ver", "asla emoji kullanma")
- Proje adı, amacı, teknoloji yığını, durumu
- Kişiler ve rolleri
- Kısaltmalar, kod adları, iç jargon
- Alınmış kararlar ve gerekçeleri
- Tekrarlayan iş akışları
- Düzeltilen hatalar ("bir daha X yapma, çünkü Y")

**Girmez:** tek seferlik görev detayı, zaten dosyada yazan şeyler (linkle),
geçici durum, **tahmin** (emin değilsen sor, uydurup yazma).

## Adımlar

1. **Mevcut hafızayı oku** (`CLAUDE.md` varsa) — tekrar yazma.
2. **Oturumu tara:** kullanıcının seni düzelttiği anlar (tercih sinyali),
   "her zaman / bir daha / biz genelde / bizde şöyle" cümleleri, açıkladığı ama
   kayıtlı olmayan isim/kısaltma/proje, verilen kararlar.
3. **Öner, sonra yaz:**
   ```
   ## Eklemeyi öneriyorum
   § Bölüm → "eklenecek satır"   [neden: oturumda şunu dedin]
   ## Güncellemeyi öneriyorum
   § Bölüm → eski: "..." → yeni: "..."
   ```
   Onay al, sonra uygula.
4. **Yerine koy.** Doğru bölüme yaz, mevcut yapıyı bozma.
5. **Buda.** Dosya 200 satırı geçtiğinde: geçersiz satırları sil, tekrarları
   birleştir, detay şişmişse ayrı dosyaya taşı ve linkle. Silmeden önce göster.

## Kurallar
- **Kısa yaz.** Hafıza her oturumda okunuyor; şişerse maliyetli ve etkisiz olur.
- Kontrol edilebilir yaz: "raporlar PDF" ✅ / "kullanıcı düzeni sever" ❌
- Hassas veri (şifre, API anahtarı, kimlik no, banka bilgisi) **asla** yazma.
- Karar defterine eklerken tarih at.

Hafıza dosyası yoksa: nerede tutulacağını sor, sonra oluştur.

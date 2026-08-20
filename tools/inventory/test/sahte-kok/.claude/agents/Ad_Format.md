---
name: Ad_Format
description: Sahte kökte ad biçim kuralını doğrulamak için hazırlanmış örnek agent tanımı; frontmatter içindeki name alanı bilerek büyük harf ve alt çizgi içerir, dosya adıyla birebir aynıdır ve yalnızca R04 kuralını tetiklemesi beklenir.
tools: Read, Grep
model: sonnet
---

Bu dosyanın tek amacı R04 (ad-format) kuralının hata seviyesinde
tetiklendiğini kanıtlamaktır.

## Neden bu bozukluk

Beklenen biçim yalnız küçük harf, rakam ve tiredir. Buradaki name alanı
"Ad_Format" yazılmıştır: hem büyük harf hem alt çizgi içerir, bu yüzden
biçim kuralını ihlal eder. Dosya adı da bilerek aynı yazılmıştır ki R03
(ad-dosya-uyumu) devreye girmesin ve test çıktısında yalnız R04 görünsün.

## Diğer alanlar sağlıklı

Açıklama uzunluğu, gövde uzunluğu ve başlık sayısı bilinçli olarak sağlıklı
aralıkta tutulmuştur, böylece bu dosya yalnızca R04'ü tetikler ve test
çıktısında başka gürültü yaratmaz. Model ve araç alanları da geçerli
değerlerle doldurulmuştur, bilinmeyen hiçbir frontmatter alanı yoktur.

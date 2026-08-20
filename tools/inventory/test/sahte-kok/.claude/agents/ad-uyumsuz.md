---
name: baska-isim
description: Sahte kökte ad-dosya uyumsuzluğunu doğrulamak için hazırlanmış örnek agent tanımı; frontmatter içindeki name alanı bilerek dosya adından farklı yazılmıştır ve yalnızca R03 kuralını tetiklemesi beklenir.
tools: Read, Grep
model: sonnet
---

Bu dosyanın tek amacı R03 (ad-dosya-uyumu) kuralının hata seviyesinde
tetiklendiğini kanıtlamaktır.

## Neden bu bozukluk

Frontmatter'daki name alanı "baska-isim" olarak yazılmıştır, oysa dosya adı
"ad-uyumsuz" dur. Tarayıcı bu iki değeri karşılaştırıp uyuşmazlığı bir hata
bulgusu olarak raporlamalıdır.

## Diğer alanlar sağlıklı

Açıklama uzunluğu, gövde uzunluğu ve başlık sayısı bilinçli olarak sağlıklı
aralıkta tutulmuştur, böylece bu dosya yalnızca R03'ü tetikler ve test
çıktısında başka gürültü yaratmaz. Model ve araç alanları da geçerli
değerlerle doldurulmuştur, bilinmeyen hiçbir alan yoktur.

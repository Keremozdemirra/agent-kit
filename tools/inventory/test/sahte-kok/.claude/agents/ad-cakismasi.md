---
name: kisa-aciklama
description: Sahte kökte ad çakışmasını doğrulamak için hazırlanmış örnek agent tanımı; frontmatter içindeki name alanı bilerek kisa-aciklama.md dosyasındaki adla aynıdır ve R05 kuralını tetiklemesi beklenir.
tools: Read, Grep
model: opus
---

Bu dosyanın tek amacı R05 (ad-cakismasi) kuralının hata seviyesinde
tetiklendiğini kanıtlamaktır.

## Neden bu bozukluk

Sahte kökte zaten "kisa-aciklama" adında bir agent var. Bu dosya aynı adı
ikinci kez kullanır; iki kayıt aynı isimle çağrılamayacağı için tarayıcı
sonraki kaydı çakışma olarak işaretlemelidir.

## Beklenen yan etki

Dosya adı "ad-cakismasi", name alanı "kisa-aciklama" olduğu için bu dosya
ayrıca R03 (ad-dosya-uyumu) kuralını da tetikler. Bu kaçınılmazdır: aynı
dizinde iki dosya aynı ada sahip olamayacağından, ad çakışması ancak name
alanı dosya adından farklı yazılarak kurulabilir. R03 zaten sahte kökte
başka bir dosyayla da kapsandığı için bu yan etki test çıktısını bozmaz.

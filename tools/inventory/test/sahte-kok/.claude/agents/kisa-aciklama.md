---
name: kisa-aciklama
description: Kısa bir açıklama metni.
tools: Read
model: haiku
---

Bu dosyanın tek amacı R06 (aciklama-kalitesi) kuralının hata seviyesinde
tetiklendiğini kanıtlamaktır: frontmatter'daki description alanı 40
karakterden kısadır.

## Gövde neden dolu

Gövde bilinçli olarak uzun ve başlıklı tutulmuştur ki R07 (govde-bosluk)
kuralı bu dosya için ayrı bir bulgu üretmesin ve test çıktısı yalnızca R06
üzerine net şekilde okunabilir kalsın.

## Amaç netliği

Sahte kökteki her dosya tek bir kuralı hedefler; bu dosyanın hedefi açıkça
description alanının kısalığıdır, başka hiçbir alan bozulmamıştır.

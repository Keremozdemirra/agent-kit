---
name: kirik-ref
description: Sahte kökte kırık referans tespitini doğrulamak için hazırlanmış örnek agent tanımı; gövdede var olmayan bir agent adına backtick içinde atıf yapılmıştır ve yalnızca R08 kuralını tetiklemesi beklenir.
tools: Read, Grep
model: opus
---

Bu dosyanın tek amacı R08 (kirik-referans) kuralının uyarı seviyesinde
tetiklendiğini kanıtlamaktır.

## Kasıtlı kırık referans

Bu iş için önce olmayan bir agent çağrılmalıdır: `olmayan-agent`. Böyle bir
agent sahte kökte de gerçek kökte de tanımlı değildir. Tarayıcı bu satırda
agent kelimesi geçtiği için backtick içindeki tokeni aday referans olarak
yakalamalı ve kayıtlar arasında böyle bir ad bulamadığı için uyarı
seviyesinde bir bulgu üretmelidir.

## Diğer alanlar sağlıklı

Açıklama uzunluğu, gövde uzunluğu ve başlık sayısı bilinçli olarak sağlıklı
aralıkta tutulmuştur, böylece bu dosya yalnızca R08'i tetikler.

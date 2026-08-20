Bu dosyada bilerek frontmatter bloğu yok, düz metinle başlıyor.

Amaç, tarayıcının frontmatter_var alanını false olarak işaretlediğini ve
dogrula.py'nin R01 (frontmatter-var) kuralını hata seviyesinde ürettiğini
kanıtlamaktır. Sahte kökteki diğer dört dosyanın aksine bu dosyanın hiçbir
frontmatter alanı yok, bu yüzden ad ve aciklama alanları da boş kalacak ve
ayrıca R02 (zorunlu-alan) kuralını da tetikleyecektir — bu beklenen ve
kabul edilebilir bir yan etkidir, çünkü frontmatter'ı hiç olmayan bir
dosyanın adı ve açıklaması da olamaz.

Bu paragraf sadece gövde uzunluğunu makul bir seviyeye taşımak için
yazılmıştır, böylece R07 (govde-bosluk) kuralı bu dosya için gereksiz bir
hata ya da uyarı üretmez ve test çıktısı R01 üzerine net şekilde
okunabilir kalır. Sahte kökteki her dosya P3 test paketinde tek bir kuralı
hedefler; bu dosyanın hedefi frontmatter'ın tamamen yokluğudur.

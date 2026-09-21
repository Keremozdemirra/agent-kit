---
name: hafiza
description: Kerem'in kalıcı çalışma hafızasını yükler ve günceller. Kerem'in repoları, daily-loop otomasyonu, kişisel web sitesi, ESG/iklim/finans araçları, kariyeri, kurulu araçları ya da tercihleri hakkında herhangi bir iş yapılacaksa; "nerede kalmıştık", "devam", "hatırlıyor musun", "bunu hatırla", "hafızaya ekle" dendiğinde; ya da yeni bir sohbet önceki bir sohbetin işine devam ediyorsa kullan. Önce hafızayı oku, sonra işe başla.
---

# Hafıza

Kerem'in tek kaynak hafızası bilgisayarında duruyor. Bu sohbet onu görmüyor;
okumadan iş yapma, çünkü aksi halde önceki sohbetlerde verilmiş kararları
sıfırdan yeniden vermiş olursun.

## 1. Oku

Sohbetin başında, iş yapmadan önce:

```
mcp__remote-devices__device_bash:
  cd "$HOME/mnt/agents" && cat CLAUDE.md DEVAM.md
```

`CLAUDE.md` sıcak önbellek: kim olduğu, dil kuralı, kırmızı çizgiler, aktif
işler. `DEVAM.md` nerede kalındığı. İkisi ~150 satır, bütün sohbet geçmişini
yeniden okumaktan kat kat ucuz, bu yüzden var.

Detay gerekiyorsa, sadece gerekeni:

```
cd "$HOME/mnt/agents/memory" && cat repolar.md      # repolar ne, hangi kural
cd "$HOME/mnt/agents/memory" && cat altyapi.md      # daily-loop, secret'lar, geçmişte kırılanlar
cd "$HOME/mnt/agents/memory" && cat araclar.md      # ne kurulu, ne kurulu değil, neden
cd "$HOME/mnt/agents/memory" && cat kariyer.md      # iş arayışı, site kuralları
cd "$HOME/mnt/agents/memory" && cat kararlar.md     # verilmiş kararlar, gerekçeleriyle
```

Hepsini birden okuma. Sorulan ne ise onu.

**Bilgisayar bağlı değilse** (`device` hatası dönerse): bunu söyle, uydurma.
"Bilgisayarın kapalı, hafızayı okuyamıyorum. Claude masaüstü uygulaması
açıkken tekrar dener misin, yoksa bildiğin kadarıyla devam edeyim mi?" de.
Hafızada olduğunu varsaydığın bir şeyi hatırlıyormuş gibi yapma.

## 2. Uygula

Okuduktan sonra oradaki kurallar bu sohbette geçerlidir. Özellikle:

- **Dil:** sohbet Türkçe, üretilen her şey İngilizce.
- **Kırmızı çizgi:** başı hiçbir şekilde belaya girmeyecek. Token/API key
  hiçbir dosyaya yazılmaz. Public'e çıkan hiçbir şeyde gizli materyal olmaz.
  Gözetimsiz çalışan hiçbir şeye ihtiyacından fazla yetki verilmez.
- **Ton:** kısa, doğrudan, dolgu cümle yok, emoji yok, abartı sıfat yok.
- **Sohbet ekonomisi:** yeni sohbet açmak aynı sohbette devam etmekten ~16 kat
  pahalı. Konu başına tek sohbet. Kullanıcı küçük bir soru için yeni sohbet
  açtıysa bunu bir kez hatırlat, sonra işine bak.

## 3. Güncelle

Bu sohbette kalıcı olarak geçerli bir şey ortaya çıktıysa (yeni bir tercih,
verilmiş bir karar, biten ya da başlayan bir iş, düzeltilmiş bir hata) sohbetin
sonunda hafızaya yaz. Kalıcı olmayan tek seferlik detayı yazma.

Nereye:

| Ne | Dosya |
|---|---|
| Tercih, kırmızı çizgi, dil kuralı, karar (tarihli) | `CLAUDE.md` |
| Nerede kalındığı, açık işler, sıradaki adım | `DEVAM.md` |
| Repo bilgisi, altyapı, araç kararı, kariyer | `memory/<konu>.md` |
| Verilmiş karar + gerekçesi (tarihli) | `memory/kararlar.md` |

Yazmadan önce ne ekleyeceğini göster, onay al. Sonra:

```
mcp__remote-devices__device_bash:
  cd "$HOME/mnt/agents" && cat >> DEVAM.md <<'EOF'
  ...
  EOF
```

Karar defterine eklerken tarih at. `CLAUDE.md` 100 satırı geçiyorsa detayı
`memory/` altına indir ve buradan linkle.

**Asla yazma:** şifre, token, API anahtarı, kimlik numarası, banka bilgisi.
Bu dosyalar yedeklenip senkronlanıyor; oraya yazılan bir sır artık birden fazla
yerde demektir.

## Neden bu şekilde

Sohbetler birbirini hatırlamıyor. Hatırlıyormuş gibi yapmanın iki yolu var:
her seferinde bütün geçmişi yeniden okumak (pahalı ve giderek imkânsız) ya da
tek bir dosyayı okumak. İkincisi seçildi. Bunun bedeli, dosyanın güncel
tutulmasıdır; güncel değilse yanlış bağlam, hiç bağlam olmamasından kötüdür.

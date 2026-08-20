# Kullanım

Araç `.claude/` altındaki agent ve skill tanımlarını tarar, denetler, HTML panel üretir. **Hiçbir şeyi düzeltmez — yalnızca raporlar.** Salt-okunur.

## Komutlar
```
python3 cikti/tara.py                # envanteri JSON olarak stdout'a bas
python3 cikti/dogrula.py             # sağlık raporunu terminale bas
python3 cikti/panel.py               # cikti/rapor/panel.html üret
```

## Bayraklar
| Bayrak | Hangi komut | Ne yapar |
|---|---|---|
| `--kok <yol>` | üçü de | kök tespitini ezer |
| `--yaz` | `tara.py`, `dogrula.py` | ayrıca `cikti/rapor/*.json` yazar |
| `--json` / `--kati` / `--sessiz` | `dogrula.py` | bulgu JSON'u / uyarı da exit 1 / yalnız özet |
| `--bulgular <yol>` | `panel.py` | bulgu JSON yolu (vars.: `cikti/rapor/bulgular.json`) |
| `--cikis <yol>` | `panel.py` | çıktı HTML yolu (vars.: `cikti/rapor/panel.html`) |

## Exit kodu
`0` başarılı · `1` `dogrula.py`'de hata var (`--kati` ile uyarı da) · `2` `--kok` altında `.claude/` dizini yok (boşluğu değil, yokluğu sorun) ya da beklenmeyen istisna.

## Panel
- Başka bir köke ait bulgu dosyası **yok sayılır**: panel "denetim çalıştırılmadı"ya düşer, stderr'e uyarı basar, üst şeritte bulgu dosyasının üretim zamanı görünür.
- Okunamayan tek dosya taramayı düşürmez: hata o kaydın `frontmatter_hata` alanına yazılır, diğer kayıtlar raporlanmaya devam eder.

## Kurallar
| ID | Ad | Önem |
|---|---|---|
| R01 | frontmatter-var | hata (parse sorunu: uyarı) |
| R02 | zorunlu-alan | hata |
| R03 | ad-dosya-uyumu | hata |
| R04 | ad-format | hata |
| R05 | ad-cakismasi | hata |
| R06 | aciklama-kalitesi | hata / uyarı |
| R07 | govde-bosluk | hata / uyarı / bilgi |
| R08 | kirik-referans | uyarı |
| R09 | alan-saglik | uyarı / bilgi — `model` hiç yazılmayabilir (miras); `claude-*` tam ID de geçerli |
| R10 | eksik-skill | hata — skill klasöründe `SKILL.md` yok |

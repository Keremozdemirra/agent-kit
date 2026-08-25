#!/usr/bin/env bash
# P3 kabul testi — tara/dogrula/panel CLI'larını gerçek ve sahte kökte koşar,
# .claude/ altına hiçbir şey yazılmadığını kanıtlar. Hangi cwd'den çağrılırsa
# çağrılsın çalışır çünkü kök yolu $0 üzerinden mutlak hesaplanır, cwd'ye
# güvenilmez.
set -u

# The live .claude root the scan runs against. Override when it lives elsewhere:
#   ENVANTER_KOK=/path/to/root bash test/calistir.sh
KOK="${ENVANTER_KOK:-$HOME/Desktop/agent}"
CIKTI="$(cd "$(dirname "$0")/.." && pwd)"
SAHTE_KOK="$CIKTI/test/sahte-kok"

basarisiz() {
    echo "HATA: $1" >&2
    exit 1
}

# .claude/ altındaki her *.md dosyanın (agent + skill) yol|mtime|boyut
# imzasını basar. Salt-okunurluğu kanıtlamak için önce/sonra karşılaştırılır.
imza_al() {
    python3 -c "
import pathlib
kok = pathlib.Path('$KOK')
dosyalar = sorted(kok.glob('.claude/agents/*.md')) + sorted(kok.glob('.claude/skills/*/SKILL.md'))
for p in dosyalar:
    st = p.stat()
    print('{0}|{1}|{2}'.format(p, st.st_mtime, st.st_size))
"
}

echo "== Kok: $KOK =="
echo "== Cikti: $CIKTI =="

echo "== On kosul: .claude/ altindaki dosyalarin imzasini al (salt-okunurluk kaniti icin) =="
IMZA_ONCE="$(imza_al)" || basarisiz "imza alinamadi (calistirmadan once)"

echo "== Adim 1: tara.py gecerli JSON uretiyor, sayilar.agent==10, sayilar.skill==5 =="
# --yaz: teslim edilen rapor/ anlik goruntusu her kabul kosusunda gercek
# kokten yeniden uretilsin, bayat/yabanci dosya kalmasin.
TARA_CIKTISI="$(python3 "$CIKTI/tara.py" --kok "$KOK" --yaz)" || basarisiz "tara.py calisirken hata verdi"
echo "$TARA_CIKTISI" | python3 -m json.tool > /dev/null || basarisiz "tara.py ciktisi gecerli JSON degil"
echo "$TARA_CIKTISI" | python3 -c "
import json, sys
d = json.load(sys.stdin)
assert d['sayilar'] == {'agent': 10, 'skill': 5, 'toplam': 15}, d['sayilar']
print('  OK: sayilar =', d['sayilar'])
" || basarisiz "tara.py sayilari beklenenden farkli (sahte kok gercek taramaya karismis olabilir)"

echo "== Adim 2: dogrula.py gercek kokte exit 0 donuyor =="
python3 "$CIKTI/dogrula.py" --kok "$KOK" --yaz > /dev/null
KOD=$?
[ "$KOD" -eq 0 ] || basarisiz "dogrula.py gercek kokte exit $KOD dondu, 0 beklendi"
echo "  OK: exit 0"

echo "== Adim 3: dogrula.py sahte kokte exit 1 donuyor, 9 kuralin TAMAMI tetikleniyor =="
python3 "$CIKTI/dogrula.py" --kok "$SAHTE_KOK" > /dev/null
KOD=$?
[ "$KOD" -eq 1 ] || basarisiz "dogrula.py sahte kokte exit $KOD dondu, 1 beklendi"
BULGU_CIKTISI="$(python3 "$CIKTI/dogrula.py" --kok "$SAHTE_KOK" --json)"
KOD_JSON=$?
# --json de hata varsa exit 1 doner (KOD ile ayni anlamda) — bu beklenen,
# yalnizca beklenmedik exit 2 (istisna) burada gercek basarisizliktir.
[ "$KOD_JSON" -eq 1 ] || basarisiz "dogrula.py --json beklenmeyen exit $KOD_JSON dondu"
echo "$BULGU_CIKTISI" | python3 -c "
import json, sys
d = json.load(sys.stdin)
ids = {b['kural'] for b in d['bulgular']}
# TAM kume: 'en az N' esigi, fixture silinince testin sessizce gecmesine
# izin veriyordu. Eksik ya da fazla kural ID'si burada patlar.
beklenen = {'R01', 'R02', 'R03', 'R04', 'R05', 'R06', 'R07', 'R08', 'R09'}
assert ids == beklenen, 'eksik: {0} | fazla: {1}'.format(
    sorted(beklenen - ids), sorted(ids - beklenen))
assert d['ozet']['hata'] >= 3, d['ozet']
print('  OK: kural IDleri =', sorted(ids), '| hata =', d['ozet']['hata'])
" || basarisiz "sahte kok beklenen kural kumesini uretmedi"

echo "== Adim 3b: gecersiz --kok her uc CLI'da da exit 2 donuyor =="
GECERSIZ_KOK="$CIKTI/test/boyle-bir-kok-yok-$$"
for ARAC in tara dogrula panel; do
    HATA_METNI="$(python3 "$CIKTI/$ARAC.py" --kok "$GECERSIZ_KOK" 2>&1 >/dev/null)"
    KOD=$?
    [ "$KOD" -eq 2 ] || basarisiz "$ARAC.py gecersiz --kok ile exit $KOD dondu, 2 beklendi"
    case "$HATA_METNI" in
        *".claude"*) ;;
        *) basarisiz "$ARAC.py gecersiz --kok icin stderr'e aciklayici hata basmadi" ;;
    esac
done
echo "  OK: tara/dogrula/panel gecersiz kokte exit 2 + stderr hatasi"

echo "== Adim 4: panel.py cikti/rapor/panel.html uretiyor, 15 kaydin adi da geciyor =="
PANEL_STDERR="$(python3 "$CIKTI/panel.py" --kok "$KOK" 2>&1 >/dev/null)"
KOD=$?
[ "$KOD" -eq 0 ] || basarisiz "panel.py exit $KOD dondu"
# stderr sessiz olmali: buraya bir sey basiliyorsa panel bulgu dosyasini
# yok saymistir ve HTML eksik veri gosteriyordur.
[ -z "$PANEL_STDERR" ] || basarisiz "panel.py stderr'e yazdi: $PANEL_STDERR"
PANEL_HTML="$CIKTI/rapor/panel.html"
[ -s "$PANEL_HTML" ] || basarisiz "panel.html olusmadi ya da bos"
python3 -c "
import pathlib
h = pathlib.Path('$PANEL_HTML').read_text(encoding='utf-8')
adlar = ['mimar', 'uygulayici', 'entegrator', 'dogrulayici', 'kod-review',
         'hata-avcisi', 'arastirmaci', 'icerik-yazari', 'otomasyon-mimari',
         'veri-analisti', 'proje', 'karar-notu', 'inbox-triyaj',
         'gunluk-brifing', 'hafiza-guncelle']
eksik = [a for a in adlar if a not in h]
assert not eksik, eksik
print('  OK: 15 kaydin adi da panelde geciyor')
" || basarisiz "panel.html icinde beklenen kayit adlari eksik"

echo "== Adim 4b: panelde 'Genel bulgular' bolumu YOK ve gomulu JSON geri okunabiliyor =="
python3 -c "
import json, pathlib, re, sys
h = pathlib.Path('$PANEL_HTML').read_text(encoding='utf-8')
# 'Genel bulgular' = hicbir kayitla eslesmeyen bulgu var demek. Temiz
# kurulumda bu bolum cikiyorsa panel yabanci/bayat bir bulgu dosyasi okumustur.
assert 'Genel bulgular' not in h, 'panelde Genel bulgular bolumu var'
assert '0 bulgu' in h, 'ust seritte 0 bulgu yazmiyor'
# Gomulu JSON'da ham < > kalmamali (script blogu erken kapanabilir).
m = re.search(r'<script type=\"application/json\" id=\"veri\">\n(.*?)\n</script>', h, re.S)
assert m, 'gomulu veri blogu bulunamadi'
ham = m.group(1)
assert '<' not in ham and '>' not in ham, 'gomulu JSON icinde ham < ya da > var'
d = json.loads(ham)
assert len(d['kayitlar']) == 15, len(d['kayitlar'])
print('  OK: Genel bulgular yok, 0 bulgu, gomulu JSON 15 kayit ile parse edildi')
" || basarisiz "panel.html icerik dogrulamasi basarisiz"

echo "== Adim 5: .claude/ altindaki dosyalar hicbir komuttan etkilenmedi (salt-okunurluk) =="
IMZA_SONRA="$(imza_al)" || basarisiz "imza alinamadi (calistirdiktan sonra)"
[ "$IMZA_ONCE" = "$IMZA_SONRA" ] || basarisiz ".claude/ altindaki en az bir dosyanin mtime/boyutu degisti — arac salt-okunur olmali"
echo "  OK: mtime + boyut degismedi"

echo
echo "TUM KABUL KRITERLERI GECTI"
exit 0

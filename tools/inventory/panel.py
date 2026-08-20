#!/usr/bin/env python3
"""Envanter + bulguları tek dosyalık, bağımlılıksız HTML panele dönüştürür.

Kullanım:
    python3 panel.py                        # kökü otomatik bul, cikti/rapor/panel.html üret
    python3 panel.py --kok <yol>             # kök tespitini ezer
    python3 panel.py --bulgular <yol>        # bulgu JSON'unun yolunu ezer
    python3 panel.py --cikis <yol>           # çıktı HTML yolunu ezer

`dogrula.py` import edilmez/çağrılmaz — bulgular yalnız dosyadan okunur,
yoksa panel "denetim çalıştırılmadı" durumunu gösterir. Bu, P1 bitmeden
bağımsız geliştirme/çalışma için bilinçli bir tercih (bkz. 01-plan.md P2).
"""

import argparse
import html
import json
import pathlib
import re
import sys
from typing import Any, Dict, List, Optional

# __pycache__ üretme — araç salt-okunur, cikti/ altında da gereksiz artefakt
# bırakmamalı (tara.py ile aynı gerekçe).
sys.dont_write_bytecode = True

# ortak.py bu dosyayla aynı klasörde; cwd'ye bağlı kalmadan import edebilmek
# için modül dizinini sys.path'e ekliyoruz.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from ortak import KOK_BUL, ENVANTER_URET, SEMA_SURUMU, KOK_GECERLI_MI  # noqa: E402

# kurallar.py saf fonksiyon modülü (CLI değil) — dogrula.py'yi import etmeme
# kısıtını ihlal etmeden referans çözümlemede tek kaynağı paylaşıyoruz.
from kurallar import BILINEN_ADLAR, REFERANS_COZULUYOR_MU  # noqa: E402

# HTML id attribute'una girecek slug. JS tarafındaki
# String(k.kimlik).replace(/[^a-zA-Z0-9_-]/g,'-') ile AYNI kural olmak
# zorunda: aksi halde referans bağlantıları hedefi bulamaz.
_SLUG_DESENI = re.compile(r"[^a-zA-Z0-9_-]")


def _kart_id(kimlik: Any) -> str:
    return "kart-" + _SLUG_DESENI.sub("-", str(kimlik))


def _rapor_dizini() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parent / "rapor"


def _argumanlari_ayristir() -> argparse.Namespace:
    ayristirici = argparse.ArgumentParser(
        description="Agent/skill envanterini ve bulguları HTML panele dönüştürür."
    )
    ayristirici.add_argument(
        "--kok", default=None, help="Proje kökünü belirt (otomatik tespiti ezer)"
    )
    ayristirici.add_argument(
        "--bulgular",
        default=None,
        help="Bulgu JSON dosyasının yolu (varsayılan: cikti/rapor/bulgular.json)",
    )
    ayristirici.add_argument(
        "--cikis",
        default=None,
        help="Üretilecek HTML dosyasının yolu (varsayılan: cikti/rapor/panel.html)",
    )
    return ayristirici.parse_args()


def _bulgulari_oku(yol: pathlib.Path) -> Optional[Dict[str, Any]]:
    """Bulgu JSON'unu okur; dosya yoksa ya da bozuksa None döner.

    Bozuk/eksik dosyayı hata ile durdurmak yerine "denetim çalıştırılmadı"
    durumuna düşürüyoruz — panel, dogrula.py'ye bağımlı olmamalı.
    """
    if not yol.is_file():
        return None
    try:
        with open(yol, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def _bulgulari_kayitlara_dagit(
    kayitlar: List[Dict[str, Any]], bulgu_verisi: Optional[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Her kayda ilişkin bulguları ve sayaçlarını kayıt dict'ine ekler.

    kimlik'i hiçbir kayıtla eşleşmeyen (ya da null olan) bulgular ayrı bir
    "genel" kovaya düşer — 3.3 şeması kimlik'in null olabileceğini söylüyor.
    """
    kimlik_index = {r["kimlik"]: r for r in kayitlar}
    for r in kayitlar:
        r["_bulgular"] = []
        r["_bulgu_sayac"] = {"hata": 0, "uyari": 0, "bilgi": 0}

    genel_bulgular: List[Dict[str, Any]] = []
    if bulgu_verisi is not None:
        for b in bulgu_verisi.get("bulgular", []):
            hedef = kimlik_index.get(b.get("kimlik"))
            if hedef is None:
                genel_bulgular.append(b)
                continue
            hedef["_bulgular"].append(b)
            onem = b.get("onem")
            if onem in hedef["_bulgu_sayac"]:
                hedef["_bulgu_sayac"][onem] += 1

    return genel_bulgular


_STIL = """
:root {
  --bg: #0f1216;
  --panel: #171b21;
  --panel-2: #1e232b;
  --border: #2a303a;
  --text: #dfe4ea;
  --text-dim: #9aa4b2;
  --accent: #5aa9e6;
  --hata: #e5484d;
  --uyari: #e6a23c;
  --bilgi: #6b7280;
  --ok: #3fb950;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  padding: 0;
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  line-height: 1.5;
}
header.ust-serit {
  position: sticky;
  top: 0;
  z-index: 10;
  background: var(--panel);
  border-bottom: 1px solid var(--border);
  padding: 14px 20px;
}
header.ust-serit h1 {
  margin: 0 0 4px 0;
  font-size: 18px;
  font-weight: 600;
}
header.ust-serit .meta {
  color: var(--text-dim);
  font-size: 13px;
  word-break: break-all;
}
.kontroller {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
  align-items: center;
}
#arama {
  flex: 1 1 260px;
  min-width: 200px;
  background: var(--panel-2);
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--text);
  padding: 8px 10px;
  font-size: 14px;
}
button.filtre {
  background: var(--panel-2);
  border: 1px solid var(--border);
  color: var(--text);
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 13px;
  cursor: pointer;
}
button.filtre.aktif {
  background: var(--accent);
  border-color: var(--accent);
  color: #0b0f14;
  font-weight: 600;
}
button.filtre:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
main {
  max-width: 920px;
  margin: 0 auto;
  padding: 18px 20px 60px 20px;
}
.durum-basarili {
  background: var(--panel);
  border: 1px solid var(--ok);
  color: var(--ok);
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 16px;
  font-size: 14px;
}
.genel-bulgular {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 16px;
  font-size: 13px;
}
.genel-bulgular h2 {
  font-size: 14px;
  margin: 0 0 8px 0;
}
.kart {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 14px;
}
.kart-basligi {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  margin-bottom: 8px;
}
.kart-basligi h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}
.rozet {
  display: inline-block;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 10px;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}
.rozet-agent { background: #23384f; color: #7ec4ff; }
.rozet-skill { background: #2e3a24; color: #a7d675; }
.rozet-model { background: var(--panel-2); color: var(--text-dim); border: 1px solid var(--border); }
.rozet-hata { background: rgba(229,72,77,0.18); color: var(--hata); }
.rozet-uyari { background: rgba(230,162,60,0.18); color: var(--uyari); }
.rozet-bilgi { background: rgba(107,114,128,0.25); color: var(--text-dim); }
.dosya-yolu {
  font-size: 12px;
  color: var(--text-dim);
  word-break: break-all;
  margin-bottom: 10px;
}
.aciklama {
  font-size: 14px;
  word-break: break-word;
  overflow-wrap: break-word;
  margin-bottom: 10px;
}
.govde-ozet {
  font-size: 13px;
  color: var(--text-dim);
  word-break: break-word;
  overflow-wrap: break-word;
  margin-bottom: 10px;
}
.araclar {
  font-size: 12px;
  color: var(--text-dim);
  word-break: break-word;
  margin-bottom: 10px;
}
.araclar span.arac {
  display: inline-block;
  background: var(--panel-2);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 1px 6px;
  margin: 2px 4px 2px 0;
}
.bulgu-listesi {
  border-top: 1px solid var(--border);
  padding-top: 10px;
  margin-top: 4px;
}
.bulgu-satiri {
  font-size: 13px;
  padding: 6px 0;
  border-bottom: 1px dashed var(--border);
  word-break: break-word;
}
.bulgu-satiri:last-child { border-bottom: none; }
.bulgu-ipucu {
  color: var(--text-dim);
  font-size: 12px;
  margin-top: 2px;
}
section.referanslar {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 16px;
  margin-top: 24px;
}
section.referanslar h2 {
  font-size: 15px;
  margin: 0 0 10px 0;
}
.referans-satiri {
  font-size: 13px;
  padding: 5px 0;
  word-break: break-word;
}
.referans-satiri .kaynak { color: var(--text-dim); }
a.ref-ok { color: var(--accent); text-decoration: none; }
a.ref-ok:hover { text-decoration: underline; }
.ref-kirik { color: var(--hata); }
.ref-yerlesik { color: var(--text-dim); }
.bos-durum {
  color: var(--text-dim);
  font-size: 14px;
  padding: 20px;
  text-align: center;
}
"""


def _js_uret() -> str:
    # esc(): JSON içindeki ham metin JS tarafında innerHTML'e basılırken
    # kaçırılır — python tarafında html.escape yalnız doğrudan HTML'e
    # gömülen sabit alanlara (kök, zaman, sayaçlar) uygulanıyor.
    return """
(function () {
  var veri = JSON.parse(document.getElementById('veri').textContent);
  var kayitlar = veri.kayitlar;
  var container = document.getElementById('kart-listesi');
  var mevcutTurFiltre = 'hepsi';
  var mevcutArama = '';

  function esc(s) {
    if (s === null || s === undefined) return '';
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function aramaMetni(k) {
    var parcalar = [k.ad || '', k.beklenen_ad || '', k.aciklama || '',
      (k.araclar || []).join(' '), k.govde_ozet || ''];
    return parcalar.join(' ').toLowerCase();
  }

  function sorunluMu(k) {
    var s = k._bulgu_sayac;
    return s.hata + s.uyari + s.bilgi > 0;
  }

  function rozetSinifi(onem) {
    if (onem === 'hata') return 'rozet-hata';
    if (onem === 'uyari') return 'rozet-uyari';
    return 'rozet-bilgi';
  }

  function kartHtml(k) {
    // Python _kart_id() ile AYNI kural — kimlik dosya adından geliyor ve
    // tırnak/boşluk içerebilir; ham hali id attribute'una girerse
    // innerHTML uzerinden event handler enjekte edilebilir.
    var id = 'kart-' + String(k.kimlik).replace(/[^a-zA-Z0-9_-]/g, '-');
    var turRozet = k.tur === 'agent' ? 'rozet-agent' : 'rozet-skill';
    var baslik = esc(k.ad || k.beklenen_ad);
    var parcalar = [];
    parcalar.push('<article class="kart" id="' + id + '" data-tur="' + esc(k.tur) +
      '" data-sorunlu="' + (sorunluMu(k) ? '1' : '0') + '">');
    parcalar.push('<div class="kart-basligi">');
    parcalar.push('<h3>' + baslik + '</h3>');
    parcalar.push('<span class="rozet ' + turRozet + '">' + esc(k.tur) + '</span>');
    if (k.tur === 'agent' && k.model) {
      parcalar.push('<span class="rozet rozet-model">' + esc(k.model) + '</span>');
    }
    var s = k._bulgu_sayac;
    if (s.hata > 0) parcalar.push('<span class="rozet rozet-hata">' + s.hata + ' hata</span>');
    if (s.uyari > 0) parcalar.push('<span class="rozet rozet-uyari">' + s.uyari + ' uyari</span>');
    if (s.bilgi > 0) parcalar.push('<span class="rozet rozet-bilgi">' + s.bilgi + ' bilgi</span>');
    parcalar.push('</div>');
    parcalar.push('<div class="dosya-yolu">' + esc(k.dosya) + '</div>');
    parcalar.push('<div class="aciklama">' + esc(k.aciklama || '(aciklama yok)') + '</div>');
    if (k.tur === 'agent') {
      var araclarHtml = (k.araclar || []).map(function (a) {
        return '<span class="arac">' + esc(a) + '</span>';
      }).join('');
      parcalar.push('<div class="araclar">' + (araclarHtml || '(arac yok)') + '</div>');
    }
    if (k.govde_ozet) {
      parcalar.push('<div class="govde-ozet">' + esc(k.govde_ozet) + '</div>');
    }
    if (k._bulgular.length > 0) {
      parcalar.push('<div class="bulgu-listesi">');
      k._bulgular.forEach(function (b) {
        parcalar.push('<div class="bulgu-satiri">');
        parcalar.push('<span class="rozet ' + rozetSinifi(b.onem) + '">' + esc(b.kural) +
          ' ' + esc(b.onem) + '</span> ' + esc(b.mesaj));
        if (b.ipucu) {
          parcalar.push('<div class="bulgu-ipucu">-&gt; ' + esc(b.ipucu) + '</div>');
        }
        parcalar.push('</div>');
      });
      parcalar.push('</div>');
    }
    parcalar.push('</article>');
    return parcalar.join('');
  }

  function ciz() {
    var gorunecekler = kayitlar.filter(function (k) {
      if (mevcutTurFiltre === 'agent' && k.tur !== 'agent') return false;
      if (mevcutTurFiltre === 'skill' && k.tur !== 'skill') return false;
      if (mevcutTurFiltre === 'sorunlu' && !sorunluMu(k)) return false;
      if (mevcutArama && aramaMetni(k).indexOf(mevcutArama) === -1) return false;
      return true;
    });
    if (gorunecekler.length === 0) {
      container.innerHTML = '<div class="bos-durum">Eslesen kayit yok.</div>';
      return;
    }
    container.innerHTML = gorunecekler.map(kartHtml).join('');
  }

  document.getElementById('arama').addEventListener('input', function (e) {
    mevcutArama = e.target.value.trim().toLowerCase();
    ciz();
  });

  var dugmeler = document.querySelectorAll('button.filtre');
  dugmeler.forEach(function (btn) {
    btn.addEventListener('click', function () {
      if (btn.disabled) return;
      mevcutTurFiltre = btn.getAttribute('data-filtre');
      dugmeler.forEach(function (b) { b.classList.remove('aktif'); });
      btn.classList.add('aktif');
      ciz();
    });
  });

  ciz();
})();
"""


def _rozet_html(tur: str) -> str:
    sinif = "rozet-agent" if tur == "agent" else "rozet-skill"
    return '<span class="rozet {0}">{1}</span>'.format(sinif, html.escape(tur))


def _referanslar_html(kayitlar: List[Dict[str, Any]]) -> str:
    # kurallar.py R08 ile aynı anahtar ('ad') ve aynı çözümleme kuralı —
    # eskiden panel 'beklenen_ad'a bakıp yerleşik agentları bilmediği için
    # dogrula.py'nin temiz dediği referansı kırmızı gösteriyordu.
    ad_index = {r["ad"]: r for r in kayitlar if r["ad"]}
    bilinen_adlar = BILINEN_ADLAR(kayitlar)
    satirlar = []
    for r in kayitlar:
        if not r["referanslar"]:
            continue
        baglantilar = []
        for ref in r["referanslar"]:
            hedef = ad_index.get(ref)
            if hedef is not None:
                baglantilar.append(
                    '<a class="ref-ok" href="#{0}">{1}</a>'.format(
                        html.escape(_kart_id(hedef["kimlik"])), html.escape(ref)
                    )
                )
            elif REFERANS_COZULUYOR_MU(ref, bilinen_adlar):
                # Yerleşik agent: gerçek kayıt yok ama kırık da değil.
                baglantilar.append(
                    '<span class="ref-yerlesik">{0} (yerlesik)</span>'.format(
                        html.escape(ref)
                    )
                )
            else:
                baglantilar.append(
                    '<span class="ref-kirik">{0}</span>'.format(html.escape(ref))
                )
        satirlar.append(
            '<div class="referans-satiri"><span class="kaynak">{0}</span> &rarr; {1}</div>'.format(
                html.escape(r["kimlik"]), ", ".join(baglantilar)
            )
        )
    if not satirlar:
        return '<div class="bos-durum">Hicbir kayit baska bir kayda atif yapmiyor.</div>'
    return "".join(satirlar)


def _html_uret(
    kok: pathlib.Path,
    envanter: Dict[str, Any],
    bulgu_verisi: Optional[Dict[str, Any]],
    bulgu_notu: str = "",
) -> str:
    kayitlar = envanter["kayitlar"]
    genel_bulgular = _bulgulari_kayitlara_dagit(kayitlar, bulgu_verisi)

    sayilar = envanter["sayilar"]
    if bulgu_verisi is not None:
        ozet = bulgu_verisi.get("ozet", {})
        toplam_bulgu = (
            ozet.get("hata", 0) + ozet.get("uyari", 0) + ozet.get("bilgi", 0)
        )
        sayac_metni = "{0} agent &middot; {1} skill &middot; {2} bulgu ({3} hata, {4} uyari, {5} bilgi)".format(
            sayilar["agent"],
            sayilar["skill"],
            toplam_bulgu,
            ozet.get("hata", 0),
            ozet.get("uyari", 0),
            ozet.get("bilgi", 0),
        )
        # Bulgu dosyasının kendi zamanı ayrı yazılır — envanter taze olup
        # bulgular bayat olabilir, bu üst şeritte görünmeli.
        sayac_metni += " &middot; denetim: {0}".format(
            html.escape(str(bulgu_verisi.get("uretim_zamani", "bilinmiyor")))
        )
        sorunlu_devre_disi = ""
    else:
        sayac_metni = "{0} agent &middot; {1} skill &middot; denetim calistirilmadi".format(
            sayilar["agent"], sayilar["skill"]
        )
        toplam_bulgu = 0
        sorunlu_devre_disi = "disabled"

    if bulgu_verisi is not None and toplam_bulgu == 0:
        durum_html = '<div class="durum-basarili">Sorun bulunmadi &mdash; {0} kayit, denetimde bulgu yok.</div>'.format(
            sayilar["toplam"]
        )
    elif bulgu_verisi is None:
        durum_html = '<div class="genel-bulgular">Denetim calistirilmadi. Bulgulari gormek icin once <code>dogrula.py --yaz</code> calistirin.{0}</div>'.format(
            "<br>" + html.escape(bulgu_notu) if bulgu_notu else ""
        )
    else:
        durum_html = ""

    if genel_bulgular:
        genel_satirlar = "".join(
            '<div class="bulgu-satiri">{0} &mdash; {1}</div>'.format(
                html.escape(b.get("kural", "")), html.escape(b.get("mesaj", ""))
            )
            for b in genel_bulgular
        )
        durum_html += '<div class="genel-bulgular"><h2>Genel bulgular (belirli bir kayda bagli degil)</h2>{0}</div>'.format(
            genel_satirlar
        )

    panel_verisi = {
        "sema_surumu": SEMA_SURUMU,
        "kok": str(kok),
        "kayitlar": kayitlar,
    }
    # Karakter bazlı kaçış: yalnız "</" kaçırmak yetmiyordu — script-data
    # içinde "<!--" görülüp ardından "<script" gelirse HTML tokenizer
    # "double escaped" duruma geçer ve "</script>" bloğu kapatmaz.
    # < geçerli JSON'dur, json.loads aynen geri okur.
    veri_json = (
        json.dumps(panel_verisi, ensure_ascii=False, indent=2)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
    )

    referanslar_html = _referanslar_html(kayitlar)

    parcalar = []
    parcalar.append("<!DOCTYPE html>")
    parcalar.append('<html lang="tr">')
    parcalar.append("<head>")
    parcalar.append('<meta charset="utf-8">')
    parcalar.append(
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
    )
    parcalar.append("<title>Agent Envanter Paneli</title>")
    parcalar.append("<style>{0}</style>".format(_STIL))
    parcalar.append("</head>")
    parcalar.append("<body>")
    parcalar.append('<header class="ust-serit">')
    parcalar.append("<h1>Agent Envanter Paneli</h1>")
    parcalar.append(
        '<div class="meta">Kok: {0} &middot; Uretim zamani: {1}</div>'.format(
            html.escape(str(kok)), html.escape(envanter["uretim_zamani"])
        )
    )
    parcalar.append('<div class="meta">{0}</div>'.format(sayac_metni))
    parcalar.append('<div class="kontroller">')
    parcalar.append(
        '<input type="text" id="arama" placeholder="Ara: ad, aciklama, arac, govde ozeti...">'
    )
    parcalar.append(
        '<button class="filtre aktif" data-filtre="hepsi">Hepsi</button>'
    )
    parcalar.append('<button class="filtre" data-filtre="agent">Agent</button>')
    parcalar.append('<button class="filtre" data-filtre="skill">Skill</button>')
    parcalar.append(
        '<button class="filtre" data-filtre="sorunlu" {0}>Sorunlu</button>'.format(
            sorunlu_devre_disi
        )
    )
    parcalar.append("</div>")
    parcalar.append("</header>")
    parcalar.append("<main>")
    parcalar.append(durum_html)
    parcalar.append('<div id="kart-listesi"></div>')
    parcalar.append('<section class="referanslar">')
    parcalar.append("<h2>Referanslar</h2>")
    parcalar.append(referanslar_html)
    parcalar.append("</section>")
    parcalar.append("</main>")
    parcalar.append('<script type="application/json" id="veri">')
    parcalar.append(veri_json)
    parcalar.append("</script>")
    parcalar.append("<script>{0}</script>".format(_js_uret()))
    parcalar.append("</body>")
    parcalar.append("</html>")
    return "\n".join(parcalar)


def main() -> int:
    args = _argumanlari_ayristir()

    if args.kok is not None:
        kok = pathlib.Path(args.kok).resolve()
        if not KOK_GECERLI_MI(kok):
            print(
                "HATA: '{0}' altında bir '.claude/' dizini yok — kök geçersiz.".format(
                    kok
                ),
                file=sys.stderr,
            )
            return 2
    else:
        kok = KOK_BUL()

    bulgu_yolu = (
        pathlib.Path(args.bulgular).resolve()
        if args.bulgular is not None
        else _rapor_dizini() / "bulgular.json"
    )
    cikis_yolu = (
        pathlib.Path(args.cikis).resolve()
        if args.cikis is not None
        else _rapor_dizini() / "panel.html"
    )

    envanter = ENVANTER_URET(kok)
    bulgu_verisi = _bulgulari_oku(bulgu_yolu)

    # Bulgu dosyası ENVANTER_URET'in ürettiği şemadan eski/yeni bir sürüme
    # aitse (sema_surumu uyuşmuyorsa) alan adları sessizce kaymış olabilir —
    # kök uyuşmazlığıyla aynı gerekçeyle tamamen yok say.
    bulgu_notu = ""
    if (
        bulgu_verisi is not None
        and bulgu_verisi.get("sema_surumu") != SEMA_SURUMU
    ):
        bulgu_notu = (
            "Bulgu dosyasının şema sürümü uyuşmuyor (dosya: {0}, beklenen: {1}), "
            "yok sayıldı. Dosya zamanı: {2}.".format(
                bulgu_verisi.get("sema_surumu"),
                SEMA_SURUMU,
                bulgu_verisi.get("uretim_zamani", "bilinmiyor"),
            )
        )
        print(
            "UYARI: {0} Güncel şemaya uygun bulgu için 'dogrula.py --yaz' çalıştır.".format(
                bulgu_notu
            ),
            file=sys.stderr,
        )
        bulgu_verisi = None

    # dogrula.py --yaz, --kok ne olursa olsun hep aynı bulgular.json'a yazar.
    # Farklı bir köke ait bulgu dosyası okunursa hiçbir kimlik eşleşmez; onu
    # HTML'e gömmek paneli yalancı yapar (yabancı bulgular "Genel bulgular"a
    # düşer, üst şerit tertemiz kurulum için bulgu sayar). Tamamen yok say.
    if bulgu_verisi is not None and bulgu_verisi.get("kok") not in (None, str(kok)):
        bulgu_notu = (
            "Bulgu dosyası farklı bir köke ait ({0}), yok sayıldı. "
            "Dosya zamanı: {1}.".format(
                bulgu_verisi.get("kok"),
                bulgu_verisi.get("uretim_zamani", "bilinmiyor"),
            )
        )
        print(
            "UYARI: {0} Panel kökü {1}. Önce 'dogrula.py --kok {1} --yaz' çalıştır.".format(
                bulgu_notu, str(kok)
            ),
            file=sys.stderr,
        )
        bulgu_verisi = None

    html_metni = _html_uret(kok, envanter, bulgu_verisi, bulgu_notu)

    cikis_yolu.parent.mkdir(parents=True, exist_ok=True)
    with open(cikis_yolu, "w", encoding="utf-8") as f:
        f.write(html_metni)

    print(str(cikis_yolu))
    return 0


if __name__ == "__main__":
    sys.exit(main())

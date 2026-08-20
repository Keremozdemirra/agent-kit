"""Agent/skill envanteri için paylaşılan çekirdek: kök tespiti, frontmatter
parser'ı ve tarayıcı. tara.py, dogrula.py ve panel.py bu modülü import eder;
sözleşme 01-plan.md bölüm 3.1/3.2/3.4'te sabitlenmiştir, değiştirilemez.
"""

import re
import pathlib
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple

SEMA_SURUMU = "1.1"

# Beklenen agent/skill alanları — bunun dışındaki frontmatter anahtarları
# bilinmeyen_alanlar'a düşer.
_AGENT_ALANLARI = {"name", "description", "tools", "model"}
_SKILL_ALANLARI = {"name", "description"}

# Frontmatter satır deseni: yalnız İLK ':' ile böl, değer boş olabilir.
_SATIR_DESENI = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$")

# Kırık referans tespiti (bkz. plan 3.4) — bu üç kelimeden biri satırda
# geçiyorsa, o satırdaki backtick içi tokenlar aday sayılır.
_REFERANS_TETIKLEYICI = re.compile(r"agent|subagent_type|skill", re.IGNORECASE)
_BACKTICK_TOKEN = re.compile(r"`([^`]*)`")
_ADAY_DESENI = re.compile(r"^[a-z][a-z0-9-]*$")

_BASLIK_DESENI = re.compile(r"^## ", re.MULTILINE)


def KOK_BUL(baslangic: Optional[str] = None) -> pathlib.Path:
    """.claude/ klasörünü içeren en yakın üst dizini bulur.

    cwd'ye güvenilmez — varsayılan başlangıç noktası bu dosyanın (ortak.py)
    kendi konumudur, çünkü çağıran script'in cwd'si farklı olabilir ama bu
    modülün proje ağacındaki yeri sabittir.
    """
    if baslangic is None:
        baslangic_yolu = pathlib.Path(__file__).resolve()
    else:
        baslangic_yolu = pathlib.Path(baslangic).resolve()
    aday_dizin = baslangic_yolu if baslangic_yolu.is_dir() else baslangic_yolu.parent
    for ust in [aday_dizin] + list(aday_dizin.parents):
        if (ust / ".claude").is_dir():
            return ust
    raise RuntimeError(
        "'.claude' klasörü içeren bir üst dizin bulunamadı, başlangıç: "
        + str(baslangic_yolu)
    )


def KOK_GECERLI_MI(kok: pathlib.Path) -> bool:
    """kok altında bir `.claude/` DİZİNİ var mı.

    İçinin dolu olmasına bakmaz — plan boş `.claude/` dizininde çökmemeyi
    şart koşuyor; burada yalnız yazım hatası / yanlış yol yakalanır.
    """
    return (pathlib.Path(kok) / ".claude").is_dir()


def _tirnak_soy(deger: str) -> str:
    # Değer tek/çift tırnakla sarılıysa dış tırnakları kaldır — frontmatter
    # yazarken bazı description'lar tırnak içine alınmış olabilir.
    if len(deger) >= 2 and deger[0] == deger[-1] and deger[0] in ("'", '"'):
        return deger[1:-1]
    return deger


def _frontmatter_ayir(
    icerik: str,
) -> Tuple[bool, Dict[str, str], Optional[str], List[str], str]:
    """Dosya içeriğini (frontmatter_var, alanlar, hata, alan_sirasi, govde) döner.

    stdlib'de YAML parser yok; format düz `anahtar: değer` olduğu için satır
    bazlı elle parse ediyoruz.
    """
    satirlar = icerik.split("\n")
    if not satirlar or satirlar[0].strip() != "---":
        # Frontmatter bloğu hiç yok — bu bir parse hatası değil, sadece yok.
        return False, {}, None, [], icerik

    kapanis = None
    for i in range(1, len(satirlar)):
        if satirlar[i].strip() == "---":
            kapanis = i
            break
    if kapanis is None:
        return False, {}, "kapanış '---' satırı bulunamadı", [], icerik

    alanlar: Dict[str, str] = {}
    alan_sirasi: List[str] = []
    hata: Optional[str] = None
    for i in range(1, kapanis):
        satir = satirlar[i]
        eslesme = _SATIR_DESENI.match(satir)
        if eslesme is None:
            if hata is None:
                hata = "satır {0} parse edilemedi: {1!r}".format(i + 1, satir)
            continue
        anahtar = eslesme.group(1)
        deger = _tirnak_soy(eslesme.group(2).strip())
        alanlar[anahtar] = deger
        alan_sirasi.append(anahtar)

    govde = "\n".join(satirlar[kapanis + 1 :])
    return True, alanlar, hata, alan_sirasi, govde


def _referanslari_bul(govde: str) -> List[str]:
    # bkz. plan 3.4 — gerçek dosyalarda test edilmiş TAM KURAL, değiştirilemez.
    bulunanlar = set()
    for satir in govde.split("\n"):
        if _REFERANS_TETIKLEYICI.search(satir):
            for token in _BACKTICK_TOKEN.findall(satir):
                if _ADAY_DESENI.match(token):
                    bulunanlar.add(token)
    return sorted(bulunanlar)


def _govde_ozet_cikar(govde: str) -> str:
    # İlk boş-olmayan, başlık olmayan paragrafı bul; satırları tek boşlukla
    # birleştir, markdown kalın işaretini temizle, 200 karaktere kırp.
    paragraflar = re.split(r"\n\s*\n", govde.strip())
    for paragraf in paragraflar:
        satirlar = [s.strip() for s in paragraf.strip().split("\n") if s.strip()]
        satirlar = [s for s in satirlar if not s.startswith("#")]
        if not satirlar:
            continue
        birlesik = " ".join(satirlar).replace("**", "")
        return birlesik[:200]
    return ""


def _kayit_olustur(
    dosya_yolu: pathlib.Path, dosya_goreli: str, tur: str, beklenen_ad: str
) -> Dict[str, Any]:
    # utf-8-sig: BOM'lu dosyada ilk satır "﻿---" olur ve frontmatter hiç
    # görülmez — 3 sahte bulgu üretirdi. Okuma hatası tek dosyayı düşürmeli,
    # taramanın tamamını değil.
    okuma_hatasi: Optional[str] = None
    try:
        with open(dosya_yolu, "r", encoding="utf-8-sig") as f:
            icerik = f.read()
    except (OSError, UnicodeDecodeError, ValueError) as e:
        icerik = ""
        okuma_hatasi = "dosya okunamadı: {0}: {1}".format(type(e).__name__, e)

    frontmatter_var, alanlar, frontmatter_hata, alan_sirasi, govde = _frontmatter_ayir(
        icerik
    )
    if okuma_hatasi is not None:
        frontmatter_hata = okuma_hatasi

    if tur == "agent":
        beklenen_alanlar = _AGENT_ALANLARI
        model = alanlar.get("model")
        araclar_ham = alanlar.get("tools")
        araclar = (
            [t.strip() for t in araclar_ham.split(",") if t.strip()]
            if araclar_ham
            else []
        )
    else:
        beklenen_alanlar = _SKILL_ALANLARI
        model = None
        araclar = []

    ad = alanlar.get("name")
    aciklama = alanlar.get("description")

    # Sırayı koruyarak tekilleştir — aynı anahtar iki kez yazılmış olabilir.
    bilinmeyen_alanlar = list(
        dict.fromkeys(a for a in alan_sirasi if a not in beklenen_alanlar)
    )

    govde_strip = govde.strip()
    # dosya_goreli çağıran tarafından sabit şablondan üretilir; resolve()
    # edilmiş yolu kok'a göre almak .claude/ symlink olduğunda ValueError
    # ile çökerdi.
    dosya_cozulmus = dosya_yolu.resolve()
    try:
        st = dosya_yolu.stat()
        degistirilme = datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds")
    except OSError:
        degistirilme = None

    return {
        "tur": tur,
        "kimlik": "{0}:{1}".format(tur, beklenen_ad),
        "dosya": dosya_goreli,
        "dosya_mutlak": str(dosya_cozulmus),
        "beklenen_ad": beklenen_ad,
        "frontmatter_var": frontmatter_var,
        "frontmatter_hata": frontmatter_hata,
        "ad": ad,
        "aciklama": aciklama,
        "model": model,
        "araclar": araclar,
        "bilinmeyen_alanlar": bilinmeyen_alanlar,
        "aciklama_uzunluk": len(aciklama or ""),
        "govde_uzunluk": len(govde_strip),
        "govde_baslik_sayisi": len(_BASLIK_DESENI.findall(govde)),
        "govde_ozet": _govde_ozet_cikar(govde),
        "referanslar": _referanslari_bul(govde),
        "degistirilme": degistirilme,
    }


def ENVANTER_URET(kok: pathlib.Path) -> Dict[str, Any]:
    """3.2 şemasına uyan envanter dict'i döner. Dosyaları yalnız okur.

    Taranacak yollar sabit ve derin değildir (recursive glob kullanılmaz) —
    aksi halde test fixture'ları yanlışlıkla gerçek taramaya karışır.
    """
    kok = pathlib.Path(kok)
    kayitlar: List[Dict[str, Any]] = []

    agent_dizini = kok / ".claude" / "agents"
    if agent_dizini.is_dir():
        for dosya_yolu in sorted(agent_dizini.glob("*.md")):
            goreli = ".claude/agents/{0}".format(dosya_yolu.name)
            kayitlar.append(
                _kayit_olustur(dosya_yolu, goreli, "agent", dosya_yolu.stem)
            )

    # SKILL.md'si olmayan skill klasörleri hiç kayıt üretmez (glob'da
    # görünmezler) — bu yüzden ayrı bir listede tutuluyor, R10 buradan besleniyor.
    eksik_skiller: List[str] = []
    skill_dizini = kok / ".claude" / "skills"
    if skill_dizini.is_dir():
        for skill_md in sorted(skill_dizini.glob("*/SKILL.md")):
            goreli = ".claude/skills/{0}/SKILL.md".format(skill_md.parent.name)
            kayitlar.append(
                _kayit_olustur(skill_md, goreli, "skill", skill_md.parent.name)
            )
        for alt_dizin in sorted(skill_dizini.iterdir()):
            if alt_dizin.is_dir() and not (alt_dizin / "SKILL.md").is_file():
                eksik_skiller.append(alt_dizin.name)

    # Panelde ve diff'te kararlı çıktı için (tur, beklenen_ad) alfabetik sırala.
    kayitlar.sort(key=lambda r: (r["tur"], r["beklenen_ad"]))

    agent_sayisi = sum(1 for r in kayitlar if r["tur"] == "agent")
    skill_sayisi = sum(1 for r in kayitlar if r["tur"] == "skill")

    return {
        "sema_surumu": SEMA_SURUMU,
        "uretim_zamani": datetime.now().isoformat(timespec="seconds"),
        "kok": str(kok),
        "sayilar": {
            "agent": agent_sayisi,
            "skill": skill_sayisi,
            "toplam": agent_sayisi + skill_sayisi,
        },
        "kayitlar": kayitlar,
        "eksik_skiller": eksik_skiller,
    }

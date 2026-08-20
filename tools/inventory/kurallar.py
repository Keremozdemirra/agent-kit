"""10 sağlık kuralı — saf fonksiyonlar. Dosya sistemine dokunmaz, print etmez.

Girdi/çıktı şeması 01-plan.md bölüm 3.2 (envanter) ve 3.3 (bulgu) sabitlenmiş
sözleşmelerdir; panel.py bu bulgu şemasını okuyacağı için alan adı / `onem`
değeri burada değiştirilemez.
"""

import re
from typing import Any, Dict, List

# Kural ID/ad/önem tablosu 01-plan.md bölüm 4 → P1'de sabittir.
_ONEM_SIRASI = {"hata": 0, "uyari": 1, "bilgi": 2}

_AD_FORMAT_DESENI = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

_GECERLI_MODELLER = {"opus", "sonnet", "haiku", "inherit"}

# R08 — yerleşik agent adları, gerçek kayıt olmadan referans verilebilir.
# panel.py de bu listeyi import eder; iki çıktının çelişmemesi için tek kaynak.
YERLESIK_AGENTLAR = {
    "explore",
    "general-purpose",
    "plan",
    "claude",
    "statusline-setup",
    "output-style-setup",
}


def _bulgu(
    kural: str,
    kural_adi: str,
    onem: str,
    kimlik: Any,
    dosya: str,
    mesaj: str,
    ipucu: str,
) -> Dict[str, Any]:
    return {
        "kural": kural,
        "kural_adi": kural_adi,
        "onem": onem,
        "kimlik": kimlik,
        "dosya": dosya,
        "mesaj": mesaj,
        "ipucu": ipucu,
    }


def _r01_frontmatter_var(kayitlar: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    sonuc = []
    for r in kayitlar:
        if not r["frontmatter_var"] and r["frontmatter_hata"]:
            # Blok hiç okunamadı ve sebebi biliniyor (dosya okuma hatası ya da
            # kapanmayan blok) — genel "'---' ile başlamıyor" mesajı yanıltıcı.
            sonuc.append(
                _bulgu(
                    "R01",
                    "frontmatter-var",
                    "hata",
                    r["kimlik"],
                    r["dosya"],
                    "frontmatter okunamadı: {0}".format(r["frontmatter_hata"]),
                    "dosyanın utf-8 kodlu, okunabilir ve '---' bloğuyla açılıp kapanan bir metin dosyası olduğundan emin ol",
                )
            )
        elif not r["frontmatter_var"]:
            sonuc.append(
                _bulgu(
                    "R01",
                    "frontmatter-var",
                    "hata",
                    r["kimlik"],
                    r["dosya"],
                    "frontmatter bloğu bulunamadı (dosya '---' ile başlamıyor)",
                    "dosyanın en başına '---' ile açılıp '---' ile kapanan bir frontmatter bloğu ekle",
                )
            )
        elif r["frontmatter_hata"]:
            # Blok var ama içindeki bir satır parse edilemedi — tam yokluktan
            # daha hafif bir sorun, bu yüzden uyari.
            sonuc.append(
                _bulgu(
                    "R01",
                    "frontmatter-var",
                    "uyari",
                    r["kimlik"],
                    r["dosya"],
                    "frontmatter parse sorunu: {0}".format(r["frontmatter_hata"]),
                    "ilgili satırı 'anahtar: değer' biçimine getir",
                )
            )
    return sonuc


def _r02_zorunlu_alan(kayitlar: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    sonuc = []
    for r in kayitlar:
        if not r["ad"]:
            sonuc.append(
                _bulgu(
                    "R02",
                    "zorunlu-alan",
                    "hata",
                    r["kimlik"],
                    r["dosya"],
                    "frontmatter'da 'name' alanı boş ya da eksik",
                    "name: {0} satırını ekle".format(r["beklenen_ad"]),
                )
            )
        if not r["aciklama"]:
            sonuc.append(
                _bulgu(
                    "R02",
                    "zorunlu-alan",
                    "hata",
                    r["kimlik"],
                    r["dosya"],
                    "frontmatter'da 'description' alanı boş ya da eksik",
                    "description alanına ne zaman kullanılacağını açıklayan bir metin ekle",
                )
            )
    return sonuc


def _r03_ad_dosya_uyumu(kayitlar: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    sonuc = []
    for r in kayitlar:
        # ad yoksa zaten R02 bildiriyor; burada tekrar etmiyoruz.
        if r["ad"] and r["ad"] != r["beklenen_ad"]:
            if r["tur"] == "agent":
                ipucu = "name alanını '{0}' yap ya da dosyayı {0}.md olarak yeniden adlandır".format(
                    r["beklenen_ad"]
                )
            else:
                ipucu = "name alanını '{0}' yap ya da klasörü {0} olarak yeniden adlandır".format(
                    r["beklenen_ad"]
                )
            sonuc.append(
                _bulgu(
                    "R03",
                    "ad-dosya-uyumu",
                    "hata",
                    r["kimlik"],
                    r["dosya"],
                    "frontmatter'daki name '{0}' dosya adı '{1}' ile uyuşmuyor".format(
                        r["ad"], r["beklenen_ad"]
                    ),
                    ipucu,
                )
            )
    return sonuc


def _r04_ad_format(kayitlar: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    sonuc = []
    for r in kayitlar:
        if r["ad"] and not _AD_FORMAT_DESENI.match(r["ad"]):
            sonuc.append(
                _bulgu(
                    "R04",
                    "ad-format",
                    "hata",
                    r["kimlik"],
                    r["dosya"],
                    "name '{0}' beklenen biçime uymuyor (küçük harf, rakam, tire)".format(
                        r["ad"]
                    ),
                    "name alanını yalnız küçük harf, rakam ve tireden oluşacak şekilde düzelt",
                )
            )
    return sonuc


def _r05_ad_cakismasi(kayitlar: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    sonuc = []
    gruplar: Dict[str, List[Dict[str, Any]]] = {}
    for r in kayitlar:
        if r["ad"]:
            gruplar.setdefault(r["ad"], []).append(r)
    for ad, kayit_listesi in gruplar.items():
        if len(kayit_listesi) <= 1:
            continue
        # İlk kaydı "asıl" say, sonrakileri çakışma olarak işaretle — kimlik
        # her zaman dolu tutulur (bkz. plan 3.3).
        sirali = sorted(kayit_listesi, key=lambda r: r["kimlik"])
        asil = sirali[0]
        for r in sirali[1:]:
            sonuc.append(
                _bulgu(
                    "R05",
                    "ad-cakismasi",
                    "hata",
                    r["kimlik"],
                    r["dosya"],
                    "name '{0}' başka bir kayıtla çakışıyor ({1})".format(
                        ad, asil["kimlik"]
                    ),
                    "iki kayıttan birinin name alanını benzersiz yap",
                )
            )
    return sonuc


def _r06_aciklama_kalitesi(kayitlar: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    sonuc = []
    for r in kayitlar:
        aciklama = r["aciklama"]
        if aciklama is None:
            continue  # eksiklik zaten R02'de bildiriliyor
        uzunluk = r["aciklama_uzunluk"]
        if uzunluk < 40:
            sonuc.append(
                _bulgu(
                    "R06",
                    "aciklama-kalitesi",
                    "hata",
                    r["kimlik"],
                    r["dosya"],
                    "aciklama {0} karakter, 40 karakterden kısa".format(uzunluk),
                    "açıklamaya ne işe yaradığını ve ne zaman kullanılacağını anlatan ayrıntı ekle",
                )
            )
        elif 40 <= uzunluk <= 119:
            sonuc.append(
                _bulgu(
                    "R06",
                    "aciklama-kalitesi",
                    "uyari",
                    r["kimlik"],
                    r["dosya"],
                    "aciklama {0} karakter, 40-119 aralığında — biraz kısa".format(
                        uzunluk
                    ),
                    "açıklamaya ne zaman tetiklendiğini gösteren 1-2 örnek daha ekle",
                )
            )
        elif uzunluk > 1024:
            sonuc.append(
                _bulgu(
                    "R06",
                    "aciklama-kalitesi",
                    "uyari",
                    r["kimlik"],
                    r["dosya"],
                    "aciklama {0} karakter, 1024'ten uzun".format(uzunluk),
                    "açıklamayı özünde kalacak şekilde kısalt",
                )
            )
        # Satır bazlı parser değere '\n' koyamaz; asıl yakalanmak istenen şey
        # description'ın çok satırlı YAML skaler işaretiyle açılmış olması.
        if aciklama.strip() in (">", "|", ">-", "|-", ">+", "|+"):
            sonuc.append(
                _bulgu(
                    "R06",
                    "aciklama-kalitesi",
                    "uyari",
                    r["kimlik"],
                    r["dosya"],
                    "description çok satırlı YAML skaleri ('{0}') ile açılmış, içerik okunamıyor".format(
                        aciklama.strip()
                    ),
                    "description alanını tek satıra sığacak şekilde yeniden yaz",
                )
            )
    return sonuc


def _r07_govde_bosluk(kayitlar: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    sonuc = []
    for r in kayitlar:
        uzunluk = r["govde_uzunluk"]
        if uzunluk < 200:
            sonuc.append(
                _bulgu(
                    "R07",
                    "govde-bosluk",
                    "hata",
                    r["kimlik"],
                    r["dosya"],
                    "gövde {0} karakter, 200 karakterden kısa".format(uzunluk),
                    "gövdeye rol, kurallar ve adımları anlatan içerik ekle",
                )
            )
        elif 200 <= uzunluk <= 499:
            sonuc.append(
                _bulgu(
                    "R07",
                    "govde-bosluk",
                    "uyari",
                    r["kimlik"],
                    r["dosya"],
                    "gövde {0} karakter, 200-499 aralığında — dar".format(uzunluk),
                    "gövdeyi rol tanımı ve somut kurallarla genişlet",
                )
            )
        if r["govde_baslik_sayisi"] == 0:
            sonuc.append(
                _bulgu(
                    "R07",
                    "govde-bosluk",
                    "bilgi",
                    r["kimlik"],
                    r["dosya"],
                    "gövdede '## ' ile başlayan başlık yok",
                    "içeriği bölümlere ayırmak için '## ' başlıkları ekle",
                )
            )
    return sonuc


def BILINEN_ADLAR(kayitlar: List[Dict[str, Any]]) -> set:
    """Referans çözümlemede kullanılan ad kümesi (frontmatter 'name' alanı)."""
    return {r["ad"] for r in kayitlar if r["ad"]}


def REFERANS_COZULUYOR_MU(ref: str, bilinen_adlar: set) -> bool:
    """R08'in referans çözümleme kuralı. panel.py de bunu çağırır."""
    return ref in bilinen_adlar or ref.lower() in YERLESIK_AGENTLAR


def _r08_kirik_referans(kayitlar: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    sonuc = []
    bilinen_adlar = BILINEN_ADLAR(kayitlar)
    for r in kayitlar:
        for ref in r["referanslar"]:
            if REFERANS_COZULUYOR_MU(ref, bilinen_adlar):
                continue
            sonuc.append(
                _bulgu(
                    "R08",
                    "kirik-referans",
                    "uyari",
                    r["kimlik"],
                    r["dosya"],
                    "referanslar içinde '{0}' adında bir kayıt bulunamadı".format(ref),
                    "'{0}' adlı bir agent/skill oluştur ya da referansı gövdeden kaldır".format(
                        ref
                    ),
                )
            )
    return sonuc


def _model_gecerli(model: Any) -> bool:
    """model alanı kabul edilebilir mi.

    None geçerlidir: Claude Code'da alanı hiç yazmamak 'parent'tan miras al'
    demektir, sahte uyarı üretmemeli. Tam model ID'si (claude-...) de geçerli.
    """
    if model is None:
        return True
    if model in _GECERLI_MODELLER:
        return True
    return isinstance(model, str) and model.startswith("claude-")


def _r09_alan_saglik(kayitlar: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    sonuc = []
    for r in kayitlar:
        # model ve araclar kontrolleri yalnız agent kayıtlarına uygulanır —
        # skill'de bu alanlar tanım gereği her zaman null/[] (bkz. plan 3.2).
        if r["tur"] == "agent" and not _model_gecerli(r["model"]):
            sonuc.append(
                _bulgu(
                    "R09",
                    "alan-saglik",
                    "uyari",
                    r["kimlik"],
                    r["dosya"],
                    "model '{0}' geçerli değerlerden biri değil (opus/sonnet/haiku/inherit ya da claude- ile başlayan tam model ID'si)".format(
                        r["model"]
                    ),
                    "model alanını opus, sonnet, haiku, inherit ya da tam bir claude- model ID'si yap; parent'tan miras almak için alanı tamamen kaldır",
                )
            )
        if r["tur"] == "agent" and not r["araclar"]:
            sonuc.append(
                _bulgu(
                    "R09",
                    "alan-saglik",
                    "bilgi",
                    r["kimlik"],
                    r["dosya"],
                    "araclar listesi boş",
                    "tools alanına agent'ın kullanacağı araçları ekle",
                )
            )
        if r["bilinmeyen_alanlar"]:
            sonuc.append(
                _bulgu(
                    "R09",
                    "alan-saglik",
                    "bilgi",
                    r["kimlik"],
                    r["dosya"],
                    "bilinmeyen_alanlar dolu: {0}".format(r["bilinmeyen_alanlar"]),
                    "beklenmeyen frontmatter alanını kaldır ya da kasıtlıysa göz ardı et",
                )
            )
    return sonuc


def _r10_eksik_skill(envanter: Dict[str, Any]) -> List[Dict[str, Any]]:
    """SKILL.md'si olmayan skill klasörleri — bunlar için hiç kayıt yok,
    bu yüzden envanter.eksik_skiller listesinden besleniyoruz (kayitlar'dan
    değil)."""
    sonuc = []
    for ad in envanter.get("eksik_skiller", []):
        sonuc.append(
            _bulgu(
                "R10",
                "eksik-skill",
                "hata",
                "skill:{0}".format(ad),
                ".claude/skills/{0}/".format(ad),
                "skill klasöründe SKILL.md yok",
                "klasöre bir SKILL.md dosyası ekle ya da kullanılmıyorsa klasörü kaldır",
            )
        )
    return sonuc


def KURALLARI_UYGULA(envanter: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Envanterdeki her kayda 10 kuralı uygular, 3.3 şemasına uyan bulgu listesi döner.

    Sıralama sözleşmesi: önce hata, sonra uyari, sonra bilgi; her grup içinde
    kimlik alfabetik (panel ve terminal raporu bu sırayı bekliyor).
    """
    kayitlar = envanter["kayitlar"]

    bulgular: List[Dict[str, Any]] = []
    bulgular += _r01_frontmatter_var(kayitlar)
    bulgular += _r02_zorunlu_alan(kayitlar)
    bulgular += _r03_ad_dosya_uyumu(kayitlar)
    bulgular += _r04_ad_format(kayitlar)
    bulgular += _r05_ad_cakismasi(kayitlar)
    bulgular += _r06_aciklama_kalitesi(kayitlar)
    bulgular += _r07_govde_bosluk(kayitlar)
    bulgular += _r08_kirik_referans(kayitlar)
    bulgular += _r09_alan_saglik(kayitlar)
    bulgular += _r10_eksik_skill(envanter)

    bulgular.sort(key=lambda b: (_ONEM_SIRASI[b["onem"]], b["kimlik"] or ""))
    return bulgular

#!/usr/bin/env python3
"""Envanteri 9 sağlık kuralına göre denetler, terminale rapor basar.

Kullanım:
    python3 dogrula.py                 # kökü otomatik bul, terminal raporu bas
    python3 dogrula.py --kok <yol>     # kök tespitini ezer
    python3 dogrula.py --json          # bulgu JSON'unu (3.3 şeması) stdout'a bas
    python3 dogrula.py --yaz           # ek olarak cikti/rapor/bulgular.json'a yaz
    python3 dogrula.py --kati          # uyarılar da exit 1 üretir
    python3 dogrula.py --sessiz        # yalnız özet satırını bas

Exit kodu: hata varsa 1 (--kati ile uyarı da 1 üretir), aksi halde 0,
beklenmeyen istisna 2. Araç hiçbir şeyi düzeltmez, yalnız raporlar.
"""

import argparse
import json
import pathlib
import sys
from datetime import datetime
from typing import Any, Dict, List, Tuple

# __pycache__ üretme — araç salt-okunur, cikti/ altında da gereksiz artefakt
# bırakmamalı.
sys.dont_write_bytecode = True

# ortak.py ve kurallar.py bu dosyayla aynı klasörde; cwd'ye bağlı kalmadan
# import edebilmek için modül dizinini sys.path'e ekliyoruz.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from ortak import KOK_BUL, ENVANTER_URET, SEMA_SURUMU, KOK_GECERLI_MI  # noqa: E402
from kurallar import KURALLARI_UYGULA  # noqa: E402

_ETIKET = {"hata": "HATA", "uyari": "UYARI", "bilgi": "BİLGİ"}


def _argumanlari_ayristir() -> argparse.Namespace:
    ayristirici = argparse.ArgumentParser(
        description="Agent/skill envanterini sağlık kurallarına göre denetler."
    )
    ayristirici.add_argument(
        "--kok", default=None, help="Proje kökünü belirt (otomatik tespiti ezer)"
    )
    ayristirici.add_argument(
        "--json", action="store_true", help="Bulgu JSON'unu stdout'a bas"
    )
    ayristirici.add_argument(
        "--yaz",
        action="store_true",
        help="Bulgu JSON'unu ayrıca cikti/rapor/bulgular.json dosyasına yaz",
    )
    ayristirici.add_argument(
        "--kati",
        action="store_true",
        help="Uyarılar da varsa exit kodu 1 döner (varsayılan: yalnız hata)",
    )
    ayristirici.add_argument(
        "--sessiz", action="store_true", help="Terminal raporunda yalnız özet satırını bas"
    )
    return ayristirici.parse_args()


def _ozet_hesapla(bulgular: List[Dict[str, Any]]) -> Tuple[int, int, int]:
    hata = sum(1 for b in bulgular if b["onem"] == "hata")
    uyari = sum(1 for b in bulgular if b["onem"] == "uyari")
    bilgi = sum(1 for b in bulgular if b["onem"] == "bilgi")
    return hata, uyari, bilgi


def _bulgu_json_olustur(
    kok: str, bulgular: List[Dict[str, Any]], toplam: int
) -> Dict[str, Any]:
    hata, uyari, bilgi = _ozet_hesapla(bulgular)
    return {
        "sema_surumu": SEMA_SURUMU,
        "uretim_zamani": datetime.now().isoformat(timespec="seconds"),
        "kok": kok,
        "ozet": {
            "hata": hata,
            "uyari": uyari,
            "bilgi": bilgi,
            "kontrol_edilen": toplam,
        },
        "bulgular": bulgular,
    }


def _terminal_raporu_yaz(
    envanter: Dict[str, Any], bulgular: List[Dict[str, Any]], sessiz: bool
) -> None:
    hata, uyari, bilgi = _ozet_hesapla(bulgular)
    toplam = envanter["sayilar"]["toplam"]

    if sessiz:
        if bulgular:
            print("Özet: {0} hata, {1} uyarı, {2} bilgi".format(hata, uyari, bilgi))
        else:
            print("Özet: temiz — {0} kayıt, sorun yok".format(toplam))
        return

    # Renk yalnız gerçek bir terminale basılırken açık — dosyaya/boru
    # hattına yönlendirilince ANSI kaçış dizileri kirlilik yaratır.
    renkli = sys.stdout.isatty()
    renk = (
        {"hata": "\033[31m", "uyari": "\033[33m", "bilgi": "\033[36m"}
        if renkli
        else {"hata": "", "uyari": "", "bilgi": ""}
    )
    sifirla = "\033[0m" if renkli else ""

    print("Agent Envanter — Sağlık Raporu")
    print("Kök: {0}".format(envanter["kok"]))
    print(
        "Taranan: {0} agent, {1} skill".format(
            envanter["sayilar"]["agent"], envanter["sayilar"]["skill"]
        )
    )

    for onem, sayi in (("hata", hata), ("uyari", uyari), ("bilgi", bilgi)):
        grup = [b for b in bulgular if b["onem"] == onem]
        if not grup:
            continue
        print()
        print("{0}{1} ({2}){3}".format(renk[onem], _ETIKET[onem], sayi, sifirla))
        for b in grup:
            print("  [{0}] {1}  {2}".format(b["kural"], b["kimlik"], b["dosya"]))
            print("        {0}".format(b["mesaj"]))
            print("        → {0}".format(b["ipucu"]))

    print()
    if bulgular:
        print("Özet: {0} hata, {1} uyarı, {2} bilgi".format(hata, uyari, bilgi))
    else:
        print("Özet: temiz — {0} kayıt, sorun yok".format(toplam))


def main() -> int:
    try:
        args = _argumanlari_ayristir()

        # --kok verildiyse kök tespiti tamamen atlanır; verilen yol doğrudan
        # kullanılır (P3'ün bozuk-kurulum testleri buna dayanır). Yolda
        # .claude/ yoksa "temiz — 0 kayıt" demek sağlık aracında yazım
        # hatasını "her şey yolunda" cevabına çevirirdi.
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

        envanter = ENVANTER_URET(kok)
        bulgular = KURALLARI_UYGULA(envanter)
        hata, uyari, _bilgi = _ozet_hesapla(bulgular)

        if args.yaz:
            rapor_dizini = pathlib.Path(__file__).resolve().parent / "rapor"
            rapor_dizini.mkdir(parents=True, exist_ok=True)
            cikti = _bulgu_json_olustur(
                envanter["kok"], bulgular, envanter["sayilar"]["toplam"]
            )
            with open(rapor_dizini / "bulgular.json", "w", encoding="utf-8") as f:
                f.write(json.dumps(cikti, ensure_ascii=False, indent=2))

        if args.json:
            cikti = _bulgu_json_olustur(
                envanter["kok"], bulgular, envanter["sayilar"]["toplam"]
            )
            print(json.dumps(cikti, ensure_ascii=False, indent=2))
        else:
            _terminal_raporu_yaz(envanter, bulgular, args.sessiz)

        if hata > 0:
            return 1
        if args.kati and (hata + uyari) > 0:
            return 1
        return 0
    except Exception as e:  # beklenmeyen istisna — plan gereği exit 2
        print("Beklenmeyen hata: {0}".format(e), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

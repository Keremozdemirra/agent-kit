#!/usr/bin/env python3
"""Envanteri tarar ve geçerli JSON olarak stdout'a basar.

Kullanım:
    python3 tara.py                 # kökü otomatik bul, JSON'u stdout'a bas
    python3 tara.py --kok <yol>     # kök tespitini ezer
    python3 tara.py --yaz           # ek olarak cikti/rapor/envanter.json'a yaz
"""

import argparse
import json
import pathlib
import sys

# __pycache__ üretme — araç salt-okunur, cikti/ altında da gereksiz artefakt
# bırakmamalı.
sys.dont_write_bytecode = True

# ortak.py bu dosyayla aynı klasörde; cwd'ye bağlı kalmadan import edebilmek
# için modül dizinini sys.path'e ekliyoruz.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from ortak import KOK_BUL, ENVANTER_URET, KOK_GECERLI_MI  # noqa: E402


def _argumanlari_ayristir() -> argparse.Namespace:
    ayristirici = argparse.ArgumentParser(
        description="Agent/skill envanterini tarar, JSON üretir."
    )
    ayristirici.add_argument(
        "--kok", default=None, help="Proje kökünü belirt (otomatik tespiti ezer)"
    )
    ayristirici.add_argument(
        "--yaz",
        action="store_true",
        help="JSON'u ayrıca cikti/rapor/envanter.json dosyasına yaz",
    )
    return ayristirici.parse_args()


def main() -> int:
    args = _argumanlari_ayristir()

    # --kok verildiyse kök tespiti tamamen atlanır; verilen yol doğrudan
    # kullanılır (P3'ün boş/sahte dizin testleri buna dayanır). Ama yolda
    # .claude/ yoksa sessizce "0 kayıt" demek yazım hatasını gizler.
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
    metin = json.dumps(envanter, ensure_ascii=False, indent=2)

    if args.yaz:
        rapor_dizini = pathlib.Path(__file__).resolve().parent / "rapor"
        rapor_dizini.mkdir(parents=True, exist_ok=True)
        with open(rapor_dizini / "envanter.json", "w", encoding="utf-8") as f:
            f.write(metin)

    print(metin)
    return 0


if __name__ == "__main__":
    sys.exit(main())

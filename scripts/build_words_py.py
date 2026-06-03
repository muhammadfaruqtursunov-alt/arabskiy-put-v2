"""Build complete words.py from JSON files + existing Том 1 (70 hand-curated words).

Output: every word has en/uz fields (empty for new ones — bot falls back to ru).
"""
import json
import re
import sys, io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ── Том 1: 70 hand-curated words preserved verbatim ──
TOM1 = [
    {"ar": "كِتَابٌ", "tj": "китоб", "ru": "книга", "trans": "ki-taa-bun"},
    {"ar": "كُتُبٌ", "tj": "китобҳо", "ru": "книги", "trans": "ku-tu-bun"},
    {"ar": "كَاتِبٌ", "tj": "котиб", "ru": "писарь, секретарь", "trans": "kaa-ti-bun"},
    {"ar": "مَكْتَبٌ", "tj": "мактаб, миз", "ru": "стол, офис", "trans": "mak-ta-bun"},
    {"ar": "مَكْتَبَةٌ", "tj": "китобхона", "ru": "библиотека", "trans": "mak-ta-ba-tun"},
    {"ar": "مَكْتُوبٌ", "tj": "мактуб", "ru": "письмо, написанное", "trans": "mak-too-bun"},
    {"ar": "قَلَمٌ", "tj": "қалам", "ru": "ручка, карандаш", "trans": "qa-la-mun"},
    {"ar": "أَقْلَامٌ", "tj": "қаламҳо", "ru": "ручки, карандаши", "trans": "aq-laa-mun"},
    {"ar": "دَرْسٌ", "tj": "дарс", "ru": "урок", "trans": "dar-sun"},
    {"ar": "دُرُوسٌ", "tj": "дарсҳо", "ru": "уроки", "trans": "du-roo-sun"},
    {"ar": "دَفْتَرٌ", "tj": "дафтар", "ru": "тетрадь", "trans": "daf-ta-run"},
    {"ar": "مَدْرَسَةٌ", "tj": "мактаб", "ru": "школа", "trans": "mad-ra-sa-tun"},
    {"ar": "مُدَرِّسٌ", "tj": "муаллим", "ru": "учитель", "trans": "mu-dar-ri-sun"},
    {"ar": "مُدَرِّسَةٌ", "tj": "муаллима", "ru": "учительница", "trans": "mu-dar-ri-sa-tun"},
    {"ar": "بَيْتٌ", "tj": "хона", "ru": "дом", "trans": "bay-tun"},
    {"ar": "بُيُوتٌ", "tj": "хонаҳо", "ru": "дома", "trans": "bu-yoo-tun"},
    {"ar": "غُرْفَةٌ", "tj": "утоқ", "ru": "комната", "trans": "ghur-fa-tun"},
    {"ar": "غُرَفٌ", "tj": "утоқҳо", "ru": "комнаты", "trans": "ghu-ra-fun"},
    {"ar": "بَابٌ", "tj": "дар", "ru": "дверь", "trans": "baa-bun"},
    {"ar": "أَبْوَابٌ", "tj": "дарҳо", "ru": "двери", "trans": "ab-waa-bun"},
    {"ar": "نَافِذَةٌ", "tj": "тиреза", "ru": "окно", "trans": "naa-fi-dha-tun"},
    {"ar": "مِفْتَاحٌ", "tj": "калид", "ru": "ключ", "trans": "mif-taa-hun"},
    {"ar": "مَفَاتِيحٌ", "tj": "калидҳо", "ru": "ключи", "trans": "ma-faa-tee-hun"},
    {"ar": "مَفْتُوحٌ", "tj": "кушода", "ru": "открытый", "trans": "maf-too-hun"},
    {"ar": "مُغْلَقٌ", "tj": "баста", "ru": "закрытый", "trans": "mugh-la-qun"},
    {"ar": "سَرِيرٌ", "tj": "кат", "ru": "кровать", "trans": "sa-ree-run"},
    {"ar": "كُرْسِيٌّ", "tj": "курсӣ", "ru": "стул", "trans": "kur-siy-yun"},
    {"ar": "مِنْضَدَةٌ", "tj": "миз", "ru": "стол", "trans": "min-da-da-tun"},
    {"ar": "سَبُّورَةٌ", "tj": "тахтаи синф", "ru": "классная доска", "trans": "sab-boo-ra-tun"},
    {"ar": "سَاعَةٌ", "tj": "соат", "ru": "часы", "trans": "saa-a-tun"},
    {"ar": "طَالِبٌ", "tj": "донишҷӯ (м)", "ru": "студент", "trans": "taa-li-bun"},
    {"ar": "طَالِبَةٌ", "tj": "донишҷӯ (ж)", "ru": "студентка", "trans": "taa-li-ba-tun"},
    {"ar": "طُلَّابٌ", "tj": "донишҷӯён", "ru": "студенты", "trans": "tul-laa-bun"},
    {"ar": "طَبِيبٌ", "tj": "духтур (м)", "ru": "врач", "trans": "ta-bee-bun"},
    {"ar": "طَبِيبَةٌ", "tj": "духтур (ж)", "ru": "врач (ж)", "trans": "ta-bee-ba-tun"},
    {"ar": "مُسْتَشْفَى", "tj": "беморхона", "ru": "больница", "trans": "mus-tash-faa"},
    {"ar": "تَاجِرٌ", "tj": "тоҷир", "ru": "торговец", "trans": "taa-ji-run"},
    {"ar": "مُهَنْدِسٌ", "tj": "муҳандис", "ru": "инженер", "trans": "mu-han-di-sun"},
    {"ar": "فَلَّاحٌ", "tj": "деҳқон", "ru": "крестьянин", "trans": "fal-laa-hun"},
    {"ar": "وَزِيرٌ", "tj": "вазир", "ru": "министр", "trans": "wa-zee-run"},
    {"ar": "رَجُلٌ", "tj": "мард", "ru": "мужчина", "trans": "ra-ju-lun"},
    {"ar": "رِجَالٌ", "tj": "мардон", "ru": "мужчины", "trans": "ri-jaa-lun"},
    {"ar": "امْرَأَةٌ", "tj": "зан", "ru": "женщина", "trans": "im-ra-a-tun"},
    {"ar": "نِسَاءٌ", "tj": "занон", "ru": "женщины", "trans": "ni-saa-un"},
    {"ar": "وَلَدٌ", "tj": "писар", "ru": "мальчик, сын", "trans": "wa-la-dun"},
    {"ar": "أَوْلَادٌ", "tj": "фарзандон", "ru": "дети, сыновья", "trans": "aw-laa-dun"},
    {"ar": "بِنْتٌ", "tj": "духтар", "ru": "девочка, дочь", "trans": "bin-tun"},
    {"ar": "طِفْلٌ", "tj": "кӯдак", "ru": "ребёнок", "trans": "tif-lun"},
    {"ar": "فَتًى", "tj": "ҷавон (м)", "ru": "юноша", "trans": "fa-tan"},
    {"ar": "فَتَاةٌ", "tj": "духтар, ҷавон", "ru": "девушка", "trans": "fa-taa-tun"},
    {"ar": "صَدِيقٌ", "tj": "дӯст (м)", "ru": "друг", "trans": "sa-dee-qun"},
    {"ar": "صَدِيقَةٌ", "tj": "дӯст (ж)", "ru": "подруга", "trans": "sa-dee-qa-tun"},
    {"ar": "زَمِيلٌ", "tj": "ҳамкор", "ru": "коллега", "trans": "za-mee-lun"},
    {"ar": "أَبٌ", "tj": "падар", "ru": "отец", "trans": "a-bun"},
    {"ar": "أُمٌّ", "tj": "модар", "ru": "мать", "trans": "um-mun"},
    {"ar": "أَخٌ", "tj": "бародар", "ru": "брат", "trans": "a-khun"},
    {"ar": "أُخْتٌ", "tj": "хоҳар", "ru": "сестра", "trans": "ukh-tun"},
    {"ar": "ابْنٌ", "tj": "писар", "ru": "сын", "trans": "ib-nun"},
    {"ar": "ابْنَةٌ", "tj": "духтар", "ru": "дочь", "trans": "ib-na-tun"},
    {"ar": "زَوْجٌ", "tj": "шавҳар", "ru": "муж", "trans": "zaw-jun"},
    {"ar": "زَوْجَةٌ", "tj": "ҳамсар, зан", "ru": "жена", "trans": "zaw-ja-tun"},
    {"ar": "عَمٌّ", "tj": "амак", "ru": "дядя (по отцу)", "trans": "am-mun"},
    {"ar": "عَمَّةٌ", "tj": "амма", "ru": "тётя (сестра отца)", "trans": "am-ma-tun"},
    {"ar": "خَالٌ", "tj": "хол", "ru": "дядя (по матери)", "trans": "khaa-lun"},
    {"ar": "خَالَةٌ", "tj": "хола", "ru": "тётя (сестра матери)", "trans": "khaa-la-tun"},
    {"ar": "طَائِرٌ", "tj": "парранда", "ru": "птица", "trans": "taa-i-run"},
    {"ar": "عُصْفُورٌ", "tj": "гунҷишк", "ru": "воробей", "trans": "us-foo-run"},
    {"ar": "كَلْبٌ", "tj": "саг", "ru": "собака", "trans": "kal-bun"},
    {"ar": "قِطٌّ", "tj": "гурба", "ru": "кошка", "trans": "qit-tun"},
    {"ar": "حِمَارٌ", "tj": "хар", "ru": "осёл", "trans": "hi-maa-run"},
]

# Simple Arabic → Latin transliteration (no diacritics required)
TRANSLIT = {
    'ا': 'a', 'أ': 'a', 'إ': 'i', 'آ': 'aa', 'ء': "'", 'ؤ': 'u', 'ئ': 'i',
    'ب': 'b', 'ت': 't', 'ث': 'th', 'ج': 'j', 'ح': 'h', 'خ': 'kh',
    'د': 'd', 'ذ': 'dh', 'ر': 'r', 'ز': 'z', 'س': 's', 'ش': 'sh',
    'ص': 's', 'ض': 'd', 'ط': 't', 'ظ': 'z', 'ع': "'", 'غ': 'gh',
    'ف': 'f', 'ق': 'q', 'ك': 'k', 'ل': 'l', 'م': 'm', 'ن': 'n',
    'ه': 'h', 'و': 'w', 'ي': 'y', 'ى': 'a', 'ة': 'h', 'ـ': '',
    'َ': 'a', 'ُ': 'u', 'ِ': 'i',
    'ً': 'an', 'ٌ': 'un', 'ٍ': 'in',
    'ْ': '', 'ّ': '',
}


def transliterate(ar: str) -> str:
    out = []
    for c in ar:
        out.append(TRANSLIT.get(c, ''))
    s = ''.join(out)
    return re.sub(r'\s+', '-', s.strip())


def emit_word_dict(w, wid, lesson_in_book, book):
    """Format one word as a Python dict line for words.py output."""
    ar = w['ar'].replace('"', '\\"')
    tj = w['tj'].replace('"', '\\"')
    ru = w['ru'].replace('"', '\\"')
    trans = w.get('trans') or transliterate(w['ar'])
    en = w.get('en', '').replace('"', '\\"')
    uz = w.get('uz', '').replace('"', '\\"')
    return (
        f'    {{"id": {wid}, "ar": "{ar}", "trans": "{trans}", '
        f'"tj": "{tj}", "ru": "{ru}", "en": "{en}", "uz": "{uz}", '
        f'"lesson": {lesson_in_book}, "book": {book}}},'
    )


def main():
    root = Path(__file__).resolve().parent.parent
    book2 = json.load(open(root / 'scripts' / 'words_book2.json', encoding='utf-8'))
    book3 = json.load(open(root / 'scripts' / 'words_book3.json', encoding='utf-8'))

    lines = []
    wid = 1
    print(f"Том 1: {len(TOM1)} words → {(len(TOM1) + 9) // 10} lessons")
    print(f"Том 2: {len(book2)} words → {(len(book2) + 9) // 10} lessons")
    print(f"Том 3: {len(book3)} words → {(len(book3) + 9) // 10} lessons")
    print(f"Total: {len(TOM1) + len(book2) + len(book3)} words")

    for book_id, src in [(1, TOM1), (2, book2), (3, book3)]:
        lines.append(f"\n    # ── ТОМ {book_id} ──")
        for idx, w in enumerate(src):
            lesson = idx // 10 + 1
            lines.append(emit_word_dict(w, wid, lesson, book_id))
            wid += 1

    out_path = root / 'scripts' / 'generated_words_block.txt'
    out_path.write_text('\n'.join(lines), encoding='utf-8')
    print(f"\nWritten: {out_path} ({len(lines)} lines)")


if __name__ == '__main__':
    main()

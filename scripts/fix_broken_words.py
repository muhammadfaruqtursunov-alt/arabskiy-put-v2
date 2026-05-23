"""Replace broken Arabic words in words.py with hand-curated correct forms.

After running: re-read words.py to verify, then git add/commit/push.
"""
import re
import sys, io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Map: word_id -> (correct_arabic, correct_transliteration)
# Curated from Medina course context — checked against Russian translations.
FIXES = {
    # ── Ordinal numbers (book 2, lesson 4-5) ──
    105: ("الثَّانِي",   "ath-thaa-nee"),
    106: ("الثَّالِثُ",  "ath-thaa-li-thu"),
    107: ("الرَّابِعُ",  "ar-raa-bi-'u"),
    108: ("الْخَامِسُ",  "al-khaa-mi-su"),
    109: ("السَّادِسُ",  "as-saa-di-su"),
    110: ("السَّابِعُ",  "as-saa-bi-'u"),
    111: ("الثَّامِنُ",  "ath-thaa-mi-nu"),
    112: ("التَّاسِعُ",  "at-taa-si-'u"),
    113: ("الْعَاشِرُ",  "al-'aa-shi-ru"),

    # ── Common past-tense verbs ──
    117: ("أَجَابَ",     "a-jaa-ba"),       # ответил
    118: ("لَعِبَ",      "la-'i-ba"),       # играл
    119: ("قَالَ",       "qaa-la"),         # сказал
    121: ("قَامَ",       "qaa-ma"),         # встал
    122: ("كَانَ",       "kaa-na"),         # был
    130: ("قُمْ",        "qum"),            # встань
    131: ("خُذْ",        "khudh"),          # возьми

    # ── Common imperfect verbs ──
    148: ("يَحْتَاجُ",   "yah-taa-ju"),     # нуждается
    150: ("يُسَافِرُ",   "yu-saa-fi-ru"),   # путешествует
    152: ("يَصِلُ",      "ya-si-lu"),       # прибывает
    164: ("لَمَّا",      "lam-maa"),        # ещё не
    172: ("يَكَادُ",     "ya-kaa-du"),      # почти, едва
    174: ("حَاوَلَ",     "haa-wa-la"),      # попытался

    # ── Conjunctions / prepositions ──
    179: ("لِأَنَّ",     "li-an-na"),       # потому что
    180: ("لِكَيْ",      "li-kay"),         # чтобы
    181: ("كَيْ",        "kay"),            # чтобы
    182: ("لِأَجْلِ",    "li-aj-li"),       # ради, для

    # ── Attached pronouns + book ──
    183: ("كِتَابُهُ",   "ki-taa-bu-hu"),   # его книга
    184: ("كِتَابُهَا",  "ki-taa-bu-haa"),  # её книга
    185: ("كِتَابُكَ",   "ki-taa-bu-ka"),   # твоя книга (м)
    186: ("كِتَابُكِ",   "ki-taa-bu-ki"),   # твоя книга (ж)
    187: ("كِتَابُكُمْ", "ki-taa-bu-kum"),  # ваша книга
    188: ("كِتَابُنَا",  "ki-taa-bu-naa"),  # наша книга
    189: ("كِتَابُهُمْ", "ki-taa-bu-hum"),  # их книга

    # ── More verbs ──
    192: ("سَأَلَهُ",    "sa-a-la-hu"),     # спросил его
    196: ("غَبِيٌّ",     "gha-biy-yun"),    # глупый
    199: ("مَهَاجِعُ",   "ma-haa-ji-'u"),   # общежития
    203: ("فُرَقَاءُ",   "fu-ra-qaa-u"),    # группы

    # ── Vocabulary ──
    207: ("عَالِمٌ",     "'aa-li-mun"),     # учёный
    210: ("مَعَاجِمُ",   "ma-'aa-ji-mu"),   # словари
    218: ("تُفَّاحٌ",    "tuf-faa-hun"),    # яблоко
    221: ("حَيَّةٌ",     "hay-ya-tun"),     # змея
    223: ("بَقَّالٌ",    "baq-qaa-lun"),    # бакалейщик
    227: ("مَصَانِعُ",   "ma-saa-ni-'u"),   # заводы
    228: ("عَامِلٌ",     "'aa-mi-lun"),     # рабочий
    235: ("رُكَّابٌ",    "ruk-kaa-bun"),    # пассажиры
    236: ("عِمَارَةٌ",   "'i-maa-ra-tun"),  # здание
    237: ("عَمَائِرُ",   "'a-maa-i-ru"),    # здания
    239: ("سُوَرٌ",      "su-wa-run"),      # суры
    240: ("كَلِمَاتٌ",   "ka-li-maa-tun"),  # слова
    241: ("جُمَلٌ",      "ju-ma-lun"),      # предложения
    242: ("مِشْطٌ",      "mish-tun"),       # расчёска
    245: ("مَقَاعِدُ",   "ma-qaa-'i-du"),   # сиденья
    246: ("اِجْتِمَاعٌ", "ij-ti-maa-'un"),  # встреча
    247: ("قِصَّةٌ",     "qis-sa-tun"),     # рассказ
    248: ("قِصَصٌ",      "qi-sa-sun"),      # рассказы
    249: ("نَبِيٌّ",     "na-biy-yun"),     # пророк
    250: ("جَائِزَةٌ",   "jaa-i-za-tun"),   # приз
    252: ("قَاعَةٌ",     "qaa-'a-tun"),     # зал
    253: ("ثَانِيَةٌ",   "thaa-ni-ya-tun"), # секунда
    257: ("نَجَحَ",      "na-ja-ha"),       # преуспел
    258: ("رَسَبَ",      "ra-sa-ba"),       # провалился
    261: ("تِلْفَازٌ",   "til-faa-zun"),    # телевизор
    263: ("وَجَدَ",      "wa-ja-da"),       # нашёл
    264: ("طَافَ",       "taa-fa"),         # совершил таваф
    265: ("حَجَّ",       "haj-ja"),         # совершил хадж
    266: ("شَفَى",       "sha-faa"),        # исцелил
    267: ("رَضِيَ",      "ra-di-ya"),       # согласился
    268: ("شَكَا",       "sha-kaa"),        # пожаловался
    270: ("أُسَرٌ",      "u-sa-run"),       # семьи
    272: ("صَوْمٌ",      "saw-mun"),        # пост
    273: ("صِيَامٌ",     "si-yaa-mun"),     # держание поста
    274: ("جِهَاتٌ",     "ji-haa-tun"),     # стороны
    275: ("لُغَوِيٌّ",   "lu-gha-wiy-yun"), # языковой
    280: ("فِقْهٌ",      "fiq-hun"),        # фикх
    283: ("طِينٌ",       "tee-nun"),        # глина
    284: ("بَحْرٌ",      "bah-run"),        # море
    285: ("بِحَارٌ",     "bi-haa-run"),     # моря
    287: ("أَرْضٌ",      "ar-dun"),         # земля
    288: ("شَمْسٌ",      "sham-sun"),       # солнце
    289: ("نُورٌ",       "noo-run"),        # свет
    291: ("شَهْرٌ",      "shah-run"),       # месяц
    293: ("طِبٌّ",       "tib-bun"),        # медицина

    # ── Book 3 fixes ──
    314: ("فُوكَ",       "foo-ka"),         # твой рот
    315: ("كُتِبَ",      "ku-ti-ba"),       # было написано
    317: ("ضُرِبَ",      "du-ri-ba"),       # был ударен
    319: ("فُتِحَ",      "fu-ti-ha"),       # было открыто
    335: ("لَدَيْكَ",    "la-day-ka"),      # у тебя
    336: ("لَدَيْهِ",    "la-day-hi"),      # у него
    337: ("حَتَّى",      "hat-taa"),        # до, даже
    338: ("رُبَّ",       "rub-ba"),         # сколько, много
    345: ("فَوْقَ",      "faw-qa"),         # над
    346: ("تَحْتَ",      "tah-ta"),         # под
    347: ("مَرَّةً",     "mar-ra-tan"),     # один раз
    350: ("ثَمَّةَ",     "tham-ma-ta"),     # там
    351: ("إِذَا",       "i-dhaa"),         # когда, если
    352: ("لَوْ",        "law"),            # если бы
    353: ("لَوْلَا",     "law-laa"),        # если бы не
    354: ("مَنْ",        "man"),            # тот кто
    355: ("إِنْ",        "in"),             # если
    356: ("ثُمَّ",       "thum-ma"),        # затем
    357: ("أَوْ",        "aw"),             # или
    358: ("لَكِنْ",      "laa-kin"),        # однако
    359: ("أَمْ",        "am"),             # или (в вопросе)
    360: ("لَا",         "laa"),            # нет, не
    365: ("مِقَصٌّ",     "mi-qas-sun"),     # ножницы
    376: ("قَطُّ",       "qat-tu"),         # никогда
    380: ("قَدْ",        "qad"),            # уже, ведь
    382: ("كُنْتُ",      "kun-tu"),         # я был
    383: ("لَبِثَ",      "la-bi-tha"),      # задержался
    384: ("ثَمَّةَ",     "tham-ma-ta"),     # там
    385: ("حَيْثُ",      "hay-thu"),        # там где
    386: ("إِذْ",        "idh"),            # когда (прошедшее)
    388: ("مُنْذُ",      "mun-dhu"),        # с тех пор как
    389: ("مُذْ",        "mudh"),           # с (времени)
}


def apply_fixes():
    path = Path(__file__).resolve().parent.parent / 'words.py'
    src = path.read_text(encoding='utf-8')
    fixed = 0
    for wid, (ar, trans) in FIXES.items():
        # Match: {"id": NN, "ar": "...", "trans": "...",
        pattern = re.compile(
            r'(\{"id":\s*' + str(wid) + r',\s*"ar":\s*")[^"]*("\s*,\s*"trans":\s*")[^"]*(")'
        )
        new_src, n = pattern.subn(
            lambda m: m.group(1) + ar + m.group(2) + trans + m.group(3),
            src, count=1,
        )
        if n:
            src = new_src
            fixed += 1
        else:
            print(f"  WARN: id={wid} not found in words.py")
    path.write_text(src, encoding='utf-8')
    print(f"\nApplied {fixed}/{len(FIXES)} fixes to words.py")


if __name__ == '__main__':
    apply_fixes()

# -*- coding: utf-8 -*-
"""Полный словарь бота.

3 тома с разным числом слов:
    Том 1 — 70 слов, 7 уроков (базовая лексика, ручная курация)
    Том 2 — 227 слов, 23 урока (грамматика: частицы, сравнения, числа, глаголы)
    Том 3 — 111 слов, 12 уроков (грамматика: падежи, термины, новая лексика)
Всего: 408 слов из PDF "Мединский курс" Шайха Д-ра В. Абдуррахима.

Каждое слово имеет переводы на 4 языка:
    tj — таджикский (основной для Том 2/3 из PDF)
    ru — русский
    en — английский (пустые поля бот покажет на ru)
    uz — узбекский (пустые поля бот покажет на ru)

Тома НЕ блокируются — ученик выбирает любой уровень с самого начала.
Уроки нумеруются ВНУТРИ тома (1..N), а не глобально.
"""

import random
import re
import unicodedata


# ─── МЕТАДАННЫЕ ТОМОВ ─────────────────────────────────────────
BOOKS_INFO = {
    1: {
        "title_ru": "Мединский курс — Том 1",
        "title_tj": "Курси Мадина — Ҷилди 1",
        "title_en": "Medina Course — Volume 1",
        "title_uz": "Madina kursi — 1-jild",
        "author": "Д-р В. Абдуррахим",
        "level": 1,
        "level_emoji": "🟢",
        "total_lessons": 7,
    },
    2: {
        "title_ru": "Мединский курс — Том 2",
        "title_tj": "Курси Мадина — Ҷилди 2",
        "title_en": "Medina Course — Volume 2",
        "title_uz": "Madina kursi — 2-jild",
        "author": "Д-р В. Абдуррахим",
        "level": 2,
        "level_emoji": "🟡",
        "total_lessons": 23,
    },
    3: {
        "title_ru": "Мединский курс — Том 3",
        "title_tj": "Курси Мадина — Ҷилди 3",
        "title_en": "Medina Course — Volume 3",
        "title_uz": "Madina kursi — 3-jild",
        "author": "Д-р В. Абдуррахим",
        "level": 3,
        "level_emoji": "🔴",
        "total_lessons": 12,
    },
}


# ─── СЛОВАРЬ ──────────────────────────────────────────────────
WORDS = [
    # ── ТОМ 1 ──
    {"id": 1, "ar": "كِتَابٌ", "trans": "ki-taa-bun", "tj": "китоб", "ru": "книга", "en": "book", "uz": "kitob", "lesson": 1, "book": 1},
    {"id": 2, "ar": "كُتُبٌ", "trans": "ku-tu-bun", "tj": "китобҳо", "ru": "книги", "en": "books", "uz": "kitoblar", "lesson": 1, "book": 1},
    {"id": 3, "ar": "كَاتِبٌ", "trans": "kaa-ti-bun", "tj": "котиб", "ru": "писарь, секретарь", "en": "scribe, secretary, writer", "uz": "kotib, yozuvchi", "lesson": 1, "book": 1},
    {"id": 4, "ar": "مَكْتَبٌ", "trans": "mak-ta-bun", "tj": "миз", "ru": "стол, офис", "en": "desk, office", "uz": "stol, ofis", "lesson": 1, "book": 1},
    {"id": 5, "ar": "مَكْتَبَةٌ", "trans": "mak-ta-ba-tun", "tj": "китобхона", "ru": "библиотека", "en": "library", "uz": "kutubxona", "lesson": 1, "book": 1},
    {"id": 6, "ar": "مَكْتُوبٌ", "trans": "mak-too-bun", "tj": "мактуб", "ru": "письмо, написанное", "en": "letter, written", "uz": "xat, yozilgan", "lesson": 1, "book": 1},
    {"id": 7, "ar": "قَلَمٌ", "trans": "qa-la-mun", "tj": "қалам", "ru": "ручка, карандаш", "en": "pen, pencil", "uz": "ruchka, qalam", "lesson": 1, "book": 1},
    {"id": 8, "ar": "أَقْلَامٌ", "trans": "aq-laa-mun", "tj": "қаламҳо", "ru": "ручки, карандаши", "en": "pens, pencils", "uz": "ruchkalar, qalamlar", "lesson": 1, "book": 1},
    {"id": 9, "ar": "دَرْسٌ", "trans": "dar-sun", "tj": "дарс", "ru": "урок", "en": "lesson", "uz": "dars", "lesson": 1, "book": 1},
    {"id": 10, "ar": "دُرُوسٌ", "trans": "du-roo-sun", "tj": "дарсҳо", "ru": "уроки", "en": "lessons", "uz": "darslar", "lesson": 1, "book": 1},
    {"id": 11, "ar": "دَفْتَرٌ", "trans": "daf-ta-run", "tj": "дафтар", "ru": "тетрадь", "en": "notebook, exercise book", "uz": "daftar", "lesson": 2, "book": 1},
    {"id": 12, "ar": "مَدْرَسَةٌ", "trans": "mad-ra-sa-tun", "tj": "мактаб", "ru": "школа", "en": "school", "uz": "maktab", "lesson": 2, "book": 1},
    {"id": 13, "ar": "مُدَرِّسٌ", "trans": "mu-dar-ri-sun", "tj": "омӯзгор", "ru": "учитель", "en": "teacher", "uz": "oʻqituvchi, muallim", "lesson": 2, "book": 1},
    {"id": 14, "ar": "مُدَرِّسَةٌ", "trans": "mu-dar-ri-sa-tun", "tj": "муаллима", "ru": "учительница", "en": "female teacher, teacher (f)", "uz": "muallima, ayol oʻqituvchi", "lesson": 2, "book": 1},
    {"id": 15, "ar": "بَيْتٌ", "trans": "bay-tun", "tj": "хона", "ru": "дом", "en": "house, home", "uz": "uy", "lesson": 2, "book": 1},
    {"id": 16, "ar": "بُيُوتٌ", "trans": "bu-yoo-tun", "tj": "хонаҳо", "ru": "дома", "en": "houses, homes", "uz": "uylar", "lesson": 2, "book": 1},
    {"id": 17, "ar": "غُرْفَةٌ", "trans": "ghur-fa-tun", "tj": "ҳуҷра", "ru": "комната", "en": "room", "uz": "xona, hujra", "lesson": 2, "book": 1},
    {"id": 18, "ar": "غُرَفٌ", "trans": "ghu-ra-fun", "tj": "ҳуҷраҳо", "ru": "комнаты", "en": "rooms", "uz": "xonalar, hujralar", "lesson": 2, "book": 1},
    {"id": 19, "ar": "بَابٌ", "trans": "baa-bun", "tj": "дар", "ru": "дверь", "en": "door", "uz": "eshik", "lesson": 2, "book": 1},
    {"id": 20, "ar": "أَبْوَابٌ", "trans": "ab-waa-bun", "tj": "дарҳо", "ru": "двери", "en": "doors", "uz": "eshiklar", "lesson": 2, "book": 1},
    {"id": 21, "ar": "نَافِذَةٌ", "trans": "naa-fi-dha-tun", "tj": "тиреза", "ru": "окно", "en": "window", "uz": "deraza", "lesson": 3, "book": 1},
    {"id": 22, "ar": "مِفْتَاحٌ", "trans": "mif-taa-hun", "tj": "калид", "ru": "ключ", "en": "key", "uz": "kalit", "lesson": 3, "book": 1},
    {"id": 23, "ar": "مَفَاتِيحٌ", "trans": "ma-faa-tee-hun", "tj": "калидҳо", "ru": "ключи", "en": "keys", "uz": "kalitlar", "lesson": 3, "book": 1},
    {"id": 24, "ar": "مَفْتُوحٌ", "trans": "maf-too-hun", "tj": "кушода", "ru": "открытый", "en": "open", "uz": "ochiq", "lesson": 3, "book": 1},
    {"id": 25, "ar": "مُغْلَقٌ", "trans": "mugh-la-qun", "tj": "пӯшида", "ru": "закрытый", "en": "closed", "uz": "yopiq", "lesson": 3, "book": 1},
    {"id": 26, "ar": "سَرِيرٌ", "trans": "sa-ree-run", "tj": "кат, бистар", "ru": "кровать", "en": "bed", "uz": "karavot", "lesson": 3, "book": 1},
    {"id": 27, "ar": "كُرْسِيٌّ", "trans": "kur-siy-yun", "tj": "курсӣ", "ru": "стул", "en": "chair", "uz": "stul, kursi", "lesson": 3, "book": 1},
    {"id": 28, "ar": "مِنْضَدَةٌ", "trans": "min-da-da-tun", "tj": "миз", "ru": "стол", "en": "table", "uz": "stol", "lesson": 3, "book": 1},
    {"id": 29, "ar": "سَبُّورَةٌ", "trans": "sab-boo-ra-tun", "tj": "тахтача", "ru": "классная доска", "en": "blackboard, chalkboard", "uz": "doska, yozuv taxtasi", "lesson": 3, "book": 1},
    {"id": 30, "ar": "سَاعَةٌ", "trans": "saa-a-tun", "tj": "соат", "ru": "часы", "en": "clock, watch", "uz": "soat", "lesson": 3, "book": 1},
    {"id": 31, "ar": "طَالِبٌ", "trans": "taa-li-bun", "tj": "талаба, хонанда", "ru": "студент", "en": "student", "uz": "talaba, oʻquvchi", "lesson": 4, "book": 1},
    {"id": 32, "ar": "طَالِبَةٌ", "trans": "taa-li-ba-tun", "tj": "толиба", "ru": "студентка", "en": "female student, student (f)", "uz": "talaba qiz, oʻquvchi qiz", "lesson": 4, "book": 1},
    {"id": 33, "ar": "طُلَّابٌ", "trans": "tul-laa-bun", "tj": "талаба, донишҷӯ", "ru": "студенты", "en": "students", "uz": "talabalar, oʻquvchilar", "lesson": 4, "book": 1},
    {"id": 34, "ar": "طَبِيبٌ", "trans": "ta-bee-bun", "tj": "духтур", "ru": "врач", "en": "doctor, physician", "uz": "shifokor, tabib", "lesson": 4, "book": 1},
    {"id": 35, "ar": "طَبِيبَةٌ", "trans": "ta-bee-ba-tun", "tj": "духтур (зан)", "ru": "врач (ж)", "en": "doctor (f), female doctor", "uz": "shifokor (ayol), ayol shifokor", "lesson": 4, "book": 1},
    {"id": 36, "ar": "مُسْتَشْفَى", "trans": "mus-tash-faa", "tj": "беморхона", "ru": "больница", "en": "hospital", "uz": "kasalxona, shifoxona", "lesson": 4, "book": 1},
    {"id": 37, "ar": "تَاجِرٌ", "trans": "taa-ji-run", "tj": "савдогар", "ru": "торговец", "en": "merchant, trader", "uz": "savdogar, tijoratchi", "lesson": 4, "book": 1},
    {"id": 38, "ar": "مُهَنْدِسٌ", "trans": "mu-han-di-sun", "tj": "муҳандис", "ru": "инженер", "en": "engineer", "uz": "muhandis", "lesson": 4, "book": 1},
    {"id": 39, "ar": "فَلَّاحٌ", "trans": "fal-laa-hun", "tj": "деҳқон", "ru": "крестьянин", "en": "peasant, farmer", "uz": "dehqon, fermer", "lesson": 4, "book": 1},
    {"id": 40, "ar": "وَزِيرٌ", "trans": "wa-zee-run", "tj": "вазир", "ru": "министр", "en": "minister", "uz": "vazir", "lesson": 4, "book": 1},
    {"id": 41, "ar": "رَجُلٌ", "trans": "ra-ju-lun", "tj": "мард", "ru": "мужчина", "en": "man", "uz": "erkak", "lesson": 5, "book": 1},
    {"id": 42, "ar": "رِجَالٌ", "trans": "ri-jaa-lun", "tj": "мардон", "ru": "мужчины", "en": "men", "uz": "erkaklar", "lesson": 5, "book": 1},
    {"id": 43, "ar": "امْرَأَةٌ", "trans": "im-ra-a-tun", "tj": "зан", "ru": "женщина", "en": "woman", "uz": "ayol", "lesson": 5, "book": 1},
    {"id": 44, "ar": "نِسَاءٌ", "trans": "ni-saa-un", "tj": "занон", "ru": "женщины", "en": "women", "uz": "ayollar", "lesson": 5, "book": 1},
    {"id": 45, "ar": "وَلَدٌ", "trans": "wa-la-dun", "tj": "писар", "ru": "мальчик, сын", "en": "boy, son", "uz": "oʻgʻil bola, oʻgʻil", "lesson": 5, "book": 1},
    {"id": 46, "ar": "أَوْلَادٌ", "trans": "aw-laa-dun", "tj": "бача, писар", "ru": "дети, сыновья", "en": "children, sons, boys", "uz": "bolalar, oʻgʻillar, oʻgʻil bolalar", "lesson": 5, "book": 1},
    {"id": 47, "ar": "بِنْتٌ", "trans": "bin-tun", "tj": "духтар", "ru": "девочка, дочь", "en": "girl, daughter", "uz": "qiz bola, qiz", "lesson": 5, "book": 1},
    {"id": 48, "ar": "طِفْلٌ", "trans": "tif-lun", "tj": "кӯдак", "ru": "ребёнок", "en": "child", "uz": "bola, goʻdak", "lesson": 5, "book": 1},
    {"id": 49, "ar": "فَتًى", "trans": "fa-tan", "tj": "ҷавонписар", "ru": "юноша", "en": "youth, young man", "uz": "yigit, oʻspirin", "lesson": 5, "book": 1},
    {"id": 50, "ar": "فَتَاةٌ", "trans": "fa-taa-tun", "tj": "ҷавондухтар", "ru": "девушка", "en": "young woman, girl", "uz": "qiz, yosh qiz", "lesson": 5, "book": 1},
    {"id": 51, "ar": "صَدِيقٌ", "trans": "sa-dee-qun", "tj": "дӯст, рафиқ", "ru": "друг", "en": "friend", "uz": "doʻst, oʻrtoq", "lesson": 6, "book": 1},
    {"id": 52, "ar": "صَدِيقَةٌ", "trans": "sa-dee-qa-tun", "tj": "дӯст", "ru": "подруга", "en": "female friend, friend (f)", "uz": "dugona, doʻst qiz", "lesson": 6, "book": 1},
    {"id": 53, "ar": "زَمِيلٌ", "trans": "za-mee-lun", "tj": "ҳамкор, ҳамсинф", "ru": "коллега", "en": "colleague, classmate", "uz": "hamkasb, sinfdosh", "lesson": 6, "book": 1},
    {"id": 54, "ar": "أَبٌ", "trans": "a-bun", "tj": "падар", "ru": "отец", "en": "father", "uz": "ota, dada", "lesson": 6, "book": 1},
    {"id": 55, "ar": "أُمٌّ", "trans": "um-mun", "tj": "модар", "ru": "мать", "en": "mother", "uz": "ona, oyi", "lesson": 6, "book": 1},
    {"id": 56, "ar": "أَخٌ", "trans": "a-khun", "tj": "бародар", "ru": "брат", "en": "brother", "uz": "birodar, aka, uka", "lesson": 6, "book": 1},
    {"id": 57, "ar": "أُخْتٌ", "trans": "ukh-tun", "tj": "хоҳар", "ru": "сестра", "en": "sister", "uz": "opa, singil", "lesson": 6, "book": 1},
    {"id": 58, "ar": "ابْنٌ", "trans": "ib-nun", "tj": "писар", "ru": "сын", "en": "son", "uz": "oʻgʻil", "lesson": 6, "book": 1},
    {"id": 59, "ar": "ابْنَةٌ", "trans": "ib-na-tun", "tj": "духтар", "ru": "дочь", "en": "daughter", "uz": "qiz", "lesson": 6, "book": 1},
    {"id": 60, "ar": "زَوْجٌ", "trans": "zaw-jun", "tj": "шавҳар", "ru": "муж", "en": "husband", "uz": "er", "lesson": 6, "book": 1},
    {"id": 61, "ar": "زَوْجَةٌ", "trans": "zaw-ja-tun", "tj": "ҳамсар, зан", "ru": "жена", "en": "wife", "uz": "xotin, rafiqa", "lesson": 7, "book": 1},
    {"id": 62, "ar": "عَمٌّ", "trans": "am-mun", "tj": "амак", "ru": "дядя (по отцу)", "en": "uncle (father's side), paternal uncle", "uz": "amaki (ota tomondan)", "lesson": 7, "book": 1},
    {"id": 63, "ar": "عَمَّةٌ", "trans": "am-ma-tun", "tj": "амма", "ru": "тётя (сестра отца)", "en": "aunt (father's sister), paternal aunt", "uz": "amma (otaning singlisi)", "lesson": 7, "book": 1},
    {"id": 64, "ar": "خَالٌ", "trans": "khaa-lun", "tj": "тағо", "ru": "дядя (по матери)", "en": "uncle (mother's side), maternal uncle", "uz": "togʻa (ona tomondan)", "lesson": 7, "book": 1},
    {"id": 65, "ar": "خَالَةٌ", "trans": "khaa-la-tun", "tj": "хола", "ru": "тётя (сестра матери)", "en": "aunt (mother's sister), maternal aunt", "uz": "xola (onaning singlisi)", "lesson": 7, "book": 1},
    {"id": 66, "ar": "طَائِرٌ", "trans": "taa-i-run", "tj": "парранда", "ru": "птица", "en": "bird", "uz": "qush", "lesson": 7, "book": 1},
    {"id": 67, "ar": "عُصْفُورٌ", "trans": "us-foo-run", "tj": "гунҷишк", "ru": "воробей", "en": "sparrow", "uz": "chumchuq", "lesson": 7, "book": 1},
    {"id": 68, "ar": "كَلْبٌ", "trans": "kal-bun", "tj": "саг", "ru": "собака", "en": "dog", "uz": "it", "lesson": 7, "book": 1},
    {"id": 69, "ar": "قِطٌّ", "trans": "qit-tun", "tj": "гурба", "ru": "кошка", "en": "cat", "uz": "mushuk", "lesson": 7, "book": 1},
    {"id": 70, "ar": "حِمَارٌ", "trans": "hi-maa-run", "tj": "хар", "ru": "осёл", "en": "donkey", "uz": "eshak", "lesson": 7, "book": 1},

    # ── ТОМ 2 ──
    {"id": 71, "ar": "إِنَّ", "trans": "iina", "tj": "ба дурустӣ, воқеан", "ru": "поистине, воистину", "en": "indeed, truly", "uz": "haqiqatan, albatta", "lesson": 1, "book": 2},
    {"id": 72, "ar": "إِنَّهُ", "trans": "iinahu", "tj": "ба дурустӣ ӯ (м)", "ru": "поистине он", "en": "indeed he, indeed he (m)", "uz": "haqiqatan u (erkak), haqiqatan u", "lesson": 1, "book": 2},
    {"id": 73, "ar": "إِنَّهَا", "trans": "iinahaa", "tj": "ба дурустӣ ӯ (ж)", "ru": "поистине она", "en": "indeed she, indeed she (f)", "uz": "haqiqatan u (ayol), haqiqatan u", "lesson": 1, "book": 2},
    {"id": 74, "ar": "إِنَّكَ", "trans": "iinaka", "tj": "ба дурустӣ ту (м)", "ru": "поистине ты (м)", "en": "indeed you (m)", "uz": "haqiqatan sen (erkak)", "lesson": 1, "book": 2},
    {"id": 75, "ar": "إِنَّكِ", "trans": "iinaki", "tj": "ба дурустӣ ту (ж)", "ru": "поистине ты (ж)", "en": "indeed you (f)", "uz": "haqiqatan sen (ayol)", "lesson": 1, "book": 2},
    {"id": 76, "ar": "إِنَّكُمْ", "trans": "iinakum", "tj": "ба дурустӣ шумо", "ru": "поистине вы", "en": "indeed you (pl.), indeed you", "uz": "haqiqatan sizlar, haqiqatan siz", "lesson": 1, "book": 2},
    {"id": 77, "ar": "إِنَّنَا", "trans": "iinanaa", "tj": "ба дурустӣ мо", "ru": "поистине мы", "en": "indeed we", "uz": "haqiqatan biz", "lesson": 1, "book": 2},
    {"id": 78, "ar": "إِنَّهُمْ", "trans": "iinahum", "tj": "ба дурустӣ онҳо", "ru": "поистине они", "en": "indeed they", "uz": "haqiqatan ular", "lesson": 1, "book": 2},
    {"id": 79, "ar": "لَكِنَّ", "trans": "lakina", "tj": "аммо, лекин", "ru": "но, однако", "en": "but, however", "uz": "lekin, ammo, biroq", "lesson": 1, "book": 2},
    {"id": 80, "ar": "لَعَلَّ", "trans": "la'ala", "tj": "шояд", "ru": "может быть, возможно", "en": "maybe, possibly, perhaps", "uz": "balki, ehtimol", "lesson": 1, "book": 2},
    {"id": 81, "ar": "كَأَنَّ", "trans": "kaaana", "tj": "гӯё, монанд ба", "ru": "как будто, словно", "en": "as if, as though", "uz": "goʻyo, goʻyoki, xuddi", "lesson": 2, "book": 2},
    {"id": 82, "ar": "لَيْتَ", "trans": "layta", "tj": "кош (орзу)", "ru": "о если бы, хотел бы", "en": "if only, would that", "uz": "koshki, qaniydi", "lesson": 2, "book": 2},
    {"id": 83, "ar": "مُتَزَوِّجٌ", "trans": "mutzaawijun", "tj": "оиладор", "ru": "женатый", "en": "married", "uz": "uylangan, turmush qurgan", "lesson": 2, "book": 2},
    {"id": 84, "ar": "عَزَبٌ", "trans": "'azabun", "tj": "безан, муҷаррад", "ru": "холостой", "en": "single, unmarried, bachelor", "uz": "boʻydoq, uylanmagan", "lesson": 2, "book": 2},
    {"id": 85, "ar": "نَاجِحٌ", "trans": "naajihun", "tj": "наҷотёбанда, растагоршаванда", "ru": "успешный, сдавший", "en": "successful, passed", "uz": "muvaffaqiyatli, imtihondan oʻtgan", "lesson": 2, "book": 2},
    {"id": 86, "ar": "رَاسِبٌ", "trans": "raasibun", "tj": "нагузаштагӣ, фурӯ рафтан", "ru": "неуспевающий, проваливший", "en": "failing, failed", "uz": "muvaffaqiyatsiz, imtihondan yiqilgan", "lesson": 2, "book": 2},
    {"id": 87, "ar": "أَكْبَرُ", "trans": "aakbaru", "tj": "калонтар", "ru": "больше, старше", "en": "bigger, older", "uz": "kattaroq, yoshi kattaroq", "lesson": 2, "book": 2},
    {"id": 88, "ar": "أَصْغَرُ", "trans": "aasgharu", "tj": "хурдтар", "ru": "меньше, моложе", "en": "smaller, younger", "uz": "kichikroq, yoshroq", "lesson": 2, "book": 2},
    {"id": 89, "ar": "أَطْوَلُ", "trans": "aatwalu", "tj": "дарозтар, баландтар", "ru": "длиннее, выше", "en": "longer, taller", "uz": "uzunroq, balandroq", "lesson": 2, "book": 2},
    {"id": 90, "ar": "أَقْصَرُ", "trans": "aaqsaru", "tj": "кӯтоҳтар", "ru": "короче, ниже", "en": "shorter, lower", "uz": "qisqaroq, pastroq", "lesson": 2, "book": 2},
    {"id": 91, "ar": "أَجْمَلُ", "trans": "aajmalu", "tj": "зеботар", "ru": "красивее", "en": "more beautiful, prettier", "uz": "goʻzalroq, chiroyliroq", "lesson": 3, "book": 2},
    {"id": 92, "ar": "أَحْسَنُ", "trans": "aahsanu", "tj": "беҳтар", "ru": "лучше", "en": "better", "uz": "yaxshiroq", "lesson": 3, "book": 2},
    {"id": 93, "ar": "أَسْهَلُ", "trans": "aashalu", "tj": "осонтар", "ru": "легче", "en": "easier", "uz": "osonroq, yengilroq", "lesson": 3, "book": 2},
    {"id": 94, "ar": "أَصْعَبُ", "trans": "aas'abu", "tj": "душвортар", "ru": "труднее", "en": "more difficult, harder", "uz": "qiyinroq, mushkulroq", "lesson": 3, "book": 2},
    {"id": 95, "ar": "أَرْخَصُ", "trans": "aarkhasu", "tj": "арзонтар", "ru": "дешевле", "en": "cheaper", "uz": "arzonroq", "lesson": 3, "book": 2},
    {"id": 96, "ar": "أَنْظَفُ", "trans": "aanzafu", "tj": "тозатар", "ru": "чище", "en": "cleaner", "uz": "tozaroq, pokizaroq", "lesson": 3, "book": 2},
    {"id": 97, "ar": "أَبْعَدُ", "trans": "aab'adu", "tj": "дуртар", "ru": "дальше", "en": "farther, further", "uz": "uzoqroq", "lesson": 3, "book": 2},
    {"id": 98, "ar": "أَقْرَبُ", "trans": "aaqrabu", "tj": "наздиктар", "ru": "ближе", "en": "closer, nearer", "uz": "yaqinroq", "lesson": 3, "book": 2},
    {"id": 99, "ar": "أَفْضَلُ", "trans": "aafdau", "tj": "беҳтарин", "ru": "лучший, предпочтительнее", "en": "best, preferable", "uz": "eng yaxshi, afzalroq", "lesson": 3, "book": 2},
    {"id": 100, "ar": "أَكْثَرُ", "trans": "aakthrau", "tj": "бисёр, зиёд", "ru": "больше (количество)", "en": "more (quantity), more", "uz": "koʻproq (miqdor), koʻproq", "lesson": 3, "book": 2},
    {"id": 101, "ar": "أَقَلُّ", "trans": "aaqau", "tj": "кам, андак", "ru": "меньше (количество)", "en": "less (quantity), less, fewer", "uz": "kamroq (miqdor), kamroq, ozroq", "lesson": 4, "book": 2},
    {"id": 102, "ar": "سِنٌّ", "trans": "sinun", "tj": "син ну сол", "ru": "возраст, год", "en": "age, year", "uz": "yosh, yil", "lesson": 4, "book": 2},
    {"id": 103, "ar": "خَطٌّ", "trans": "khatun", "tj": "хат, навиштаҷот", "ru": "почерк, линия", "en": "handwriting, line", "uz": "xat, qoʻl yozuvi, chiziq", "lesson": 4, "book": 2},
    {"id": 104, "ar": "الأَوَّلُ", "trans": "alaawlu", "tj": "якум, нахустин, аввал", "ru": "первый", "en": "first", "uz": "birinchi", "lesson": 4, "book": 2},
    {"id": 105, "ar": "الثَّانِي", "trans": "ath-thaa-nee", "tj": "дуюм", "ru": "второй", "en": "second", "uz": "ikkinchi", "lesson": 4, "book": 2},
    {"id": 106, "ar": "الثَّالِثُ", "trans": "ath-thaa-li-thu", "tj": "сеюм", "ru": "третий", "en": "third", "uz": "uchinchi", "lesson": 4, "book": 2},
    {"id": 107, "ar": "الرَّابِعُ", "trans": "ar-raa-bi-'u", "tj": "чорум", "ru": "четвёртый", "en": "fourth", "uz": "toʻrtinchi", "lesson": 4, "book": 2},
    {"id": 108, "ar": "الْخَامِسُ", "trans": "al-khaa-mi-su", "tj": "панҷум", "ru": "пятый", "en": "fifth", "uz": "beshinchi", "lesson": 4, "book": 2},
    {"id": 109, "ar": "السَّادِسُ", "trans": "as-saa-di-su", "tj": "шашум", "ru": "шестой", "en": "sixth", "uz": "oltinchi", "lesson": 4, "book": 2},
    {"id": 110, "ar": "السَّابِعُ", "trans": "as-saa-bi-'u", "tj": "ҳафтум", "ru": "седьмой", "en": "seventh", "uz": "yettinchi", "lesson": 4, "book": 2},
    {"id": 111, "ar": "الثَّامِنُ", "trans": "ath-thaa-mi-nu", "tj": "ҳаштум", "ru": "восьмой", "en": "eighth", "uz": "sakkizinchi", "lesson": 5, "book": 2},
    {"id": 112, "ar": "التَّاسِعُ", "trans": "at-taa-si-'u", "tj": "нӯҳум", "ru": "девятый", "en": "ninth", "uz": "toʻqqizinchi", "lesson": 5, "book": 2},
    {"id": 113, "ar": "الْعَاشِرُ", "trans": "al-'aa-shi-ru", "tj": "даҳум", "ru": "десятый", "en": "tenth", "uz": "oninchi", "lesson": 5, "book": 2},
    {"id": 114, "ar": "الْجُزْءُ", "trans": "aljuz'u", "tj": "ҷузъ, қисм", "ru": "часть, том", "en": "part, volume", "uz": "qism, jild", "lesson": 5, "book": 2},
    {"id": 115, "ar": "الصَّفْحَةُ", "trans": "asfhahu", "tj": "саҳифа", "ru": "страница", "en": "page", "uz": "sahifa, bet", "lesson": 5, "book": 2},
    {"id": 116, "ar": "الدَّرَجَةُ", "trans": "adrajahu", "tj": "дараҷа", "ru": "степень, оценка", "en": "degree, grade", "uz": "daraja, baho", "lesson": 5, "book": 2},
    {"id": 117, "ar": "أَجَابَ", "trans": "a-jaa-ba", "tj": "ҷавоб дод", "ru": "ответил / отвечает", "en": "answered / answers", "uz": "javob berdi / javob beradi", "lesson": 5, "book": 2},
    {"id": 118, "ar": "لَعِبَ", "trans": "la-'i-ba", "tj": "бозид / мебозад", "ru": "играл / играет", "en": "played / plays", "uz": "oʻynadi / oʻynaydi", "lesson": 5, "book": 2},
    {"id": 119, "ar": "قَالَ", "trans": "qaa-la", "tj": "гуфт / мегӯяд", "ru": "сказал / говорит", "en": "said / says", "uz": "dedi / deydi", "lesson": 5, "book": 2},
    {"id": 120, "ar": "زَارَ", "trans": "yazuwruzaara", "tj": "Зиёрат кард", "ru": "навещал / навещает", "en": "visited / visits", "uz": "yoqladi / yoqlaydi, ziyorat qildi / ziyorat qiladi", "lesson": 5, "book": 2},
    {"id": 121, "ar": "قَامَ", "trans": "qaa-ma", "tj": "бармехезад ё рост истодан", "ru": "встал / встаёт", "en": "stood up / stands up", "uz": "turdi / turadi", "lesson": 6, "book": 2},
    {"id": 122, "ar": "كَانَ", "trans": "kaa-na", "tj": "будан, шудан", "ru": "был / является", "en": "was / is", "uz": "edi / boʻladi", "lesson": 6, "book": 2},
    {"id": 123, "ar": "اِفْتَحْ", "trans": "aiftah", "tj": "бикушо", "ru": "открой (повел.)", "en": "open (imperative)", "uz": "och (buyruq)", "lesson": 6, "book": 2},
    {"id": 124, "ar": "اُكْتُبْ", "trans": "auktub", "tj": "бинавис", "ru": "пиши", "en": "write", "uz": "yoz", "lesson": 6, "book": 2},
    {"id": 125, "ar": "اِقْرَأْ", "trans": "aiqraa", "tj": "бихон", "ru": "читай", "en": "read", "uz": "oʻqi", "lesson": 6, "book": 2},
    {"id": 126, "ar": "اِسْمَعْ", "trans": "aisma'", "tj": "бишнав", "ru": "слушай", "en": "listen, hear", "uz": "tingla, eshit", "lesson": 6, "book": 2},
    {"id": 127, "ar": "اِذْهَبْ", "trans": "aidhhab", "tj": "бирав", "ru": "иди, уходи", "en": "go, leave", "uz": "bor, ket", "lesson": 6, "book": 2},
    {"id": 128, "ar": "اُدْخُلْ", "trans": "audkhu", "tj": "дарой", "ru": "войди", "en": "enter, come in", "uz": "kir", "lesson": 6, "book": 2},
    {"id": 129, "ar": "اُخْرُجْ", "trans": "aukhruj", "tj": "барой", "ru": "выйди", "en": "go out, get out", "uz": "chiq", "lesson": 6, "book": 2},
    {"id": 130, "ar": "قُمْ", "trans": "qum", "tj": "хез, бархез", "ru": "встань", "en": "stand up, get up", "uz": "tur, oʻrningdan tur", "lesson": 6, "book": 2},
    {"id": 131, "ar": "خُذْ", "trans": "khudh", "tj": "бигир", "ru": "возьми", "en": "take", "uz": "ol", "lesson": 7, "book": 2},
    {"id": 132, "ar": "لاَ تَذْهَبْ", "trans": "tadhhablaa", "tj": "нарав", "ru": "не ходи", "en": "don't go", "uz": "borma, bormagin", "lesson": 7, "book": 2},
    {"id": 133, "ar": "لاَ تَأْكُلْ", "trans": "takulaa", "tj": "махӯр", "ru": "не ешь", "en": "don't eat", "uz": "yema, yemagin", "lesson": 7, "book": 2},
    {"id": 134, "ar": "لاَ تَكْذِبْ", "trans": "takdhiblaa", "tj": "дурӯғ нагӯ", "ru": "не лги", "en": "don't lie", "uz": "yolgʻon gapirma", "lesson": 7, "book": 2},
    {"id": 135, "ar": "لاَ تَنْزِلْ", "trans": "tanzillaa", "tj": "на фаро ба поён", "ru": "не спускайся", "en": "don't go down, don't descend", "uz": "tushma, pastga tushma", "lesson": 7, "book": 2},
    {"id": 136, "ar": "لاَ تَرْكَبْ", "trans": "tarkablaa", "tj": "савор нашав", "ru": "не садись", "en": "don't get on, don't ride", "uz": "minma", "lesson": 7, "book": 2},
    {"id": 137, "ar": "لاَ تَقْطَعْ", "trans": "taqta'laa", "tj": "набур", "ru": "не режь", "en": "don't cut", "uz": "kesma", "lesson": 7, "book": 2},
    {"id": 138, "ar": "لاَ تَرْفَعْ", "trans": "tarfa'laa", "tj": "набардор", "ru": "не поднимай", "en": "don't lift, don't raise", "uz": "koʻtarma", "lesson": 7, "book": 2},
    {"id": 139, "ar": "يَعْمَلُ", "trans": "ya'mau", "tj": "кор мекунад", "ru": "работает", "en": "works", "uz": "ishlaydi", "lesson": 7, "book": 2},
    {"id": 140, "ar": "يَسْكُنُ", "trans": "yaskunu", "tj": "сукунат кардан", "ru": "живёт, проживает", "en": "lives, resides", "uz": "yashaydi, istiqomat qiladi", "lesson": 7, "book": 2},
    {"id": 141, "ar": "يَدْرُسُ", "trans": "yadrusu", "tj": "мехонад, таҳсил мекунад", "ru": "учится, изучает", "en": "studies, learns", "uz": "oʻqiydi, oʻrganadi", "lesson": 8, "book": 2},
    {"id": 142, "ar": "يُدَرِّسُ", "trans": "yudarisu", "tj": "таълим медиҳад", "ru": "преподаёт", "en": "teaches", "uz": "dars beradi, oʻqitadi", "lesson": 8, "book": 2},
    {"id": 143, "ar": "يَفْتَحُ", "trans": "yaftahu", "tj": "мекушояд", "ru": "открывает", "en": "opens", "uz": "ochadi", "lesson": 8, "book": 2},
    {"id": 144, "ar": "يَبْحَثُ", "trans": "yabhathu", "tj": "ҷустуҷӯ мекунад", "ru": "ищет, исследовает", "en": "searches, researches", "uz": "qidiradi, tadqiq qiladi", "lesson": 8, "book": 2},
    {"id": 145, "ar": "يَعْرِفُ", "trans": "ya'rifu", "tj": "шинохтан, донистан", "ru": "знает", "en": "knows", "uz": "biladi, taniydi", "lesson": 8, "book": 2},
    {"id": 146, "ar": "يُمْكِنُ", "trans": "yumkinu", "tj": "имкон дорад, мешавад", "ru": "можно, возможно", "en": "possible, it is possible", "uz": "mumkin, imkoni bor", "lesson": 8, "book": 2},
    {"id": 147, "ar": "يُرِيدُ", "trans": "yuriydu", "tj": "мехоҳад", "ru": "хочет, желает", "en": "wants, wishes", "uz": "xohlaydi, istaydi", "lesson": 8, "book": 2},
    {"id": 148, "ar": "يَحْتَاجُ", "trans": "yah-taa-ju", "tj": "эҳтиёҷ дорад", "ru": "нуждается", "en": "needs, is in need", "uz": "muhtoj, muhtoj boʻladi, ehtiyoj sezadi", "lesson": 8, "book": 2},
    {"id": 149, "ar": "يَسْتَطِيعُ", "trans": "yastatiy'u", "tj": "метавонад", "ru": "может, способен", "en": "can, is able", "uz": "qila oladi, qodir", "lesson": 8, "book": 2},
    {"id": 150, "ar": "يُسَافِرُ", "trans": "yu-saa-fi-ru", "tj": "сафар мекунад", "ru": "путешествует", "en": "travels", "uz": "sayohat qiladi, safar qiladi", "lesson": 8, "book": 2},
    {"id": 151, "ar": "يَرْجِعُ", "trans": "yarji'u", "tj": "бармегардад", "ru": "возвращается", "en": "returns, comes back", "uz": "qaytadi, qaytib keladi", "lesson": 9, "book": 2},
    {"id": 152, "ar": "يَصِلُ", "trans": "ya-si-lu", "tj": "мерасад", "ru": "прибывает", "en": "arrives, reaches", "uz": "yetib keladi, yetib boradi", "lesson": 9, "book": 2},
    {"id": 153, "ar": "يَنْجَحُ", "trans": "yanjahu", "tj": "муваффақ мешавад", "ru": "преуспевает, сдаёт", "en": "succeeds, passes", "uz": "muvaffaq boʻladi, imtihondan oʻtadi", "lesson": 9, "book": 2},
    {"id": 154, "ar": "يَرْسُبُ", "trans": "yarsubu", "tj": "нагузаштан, таҳнишин шудан", "ru": "проваливается", "en": "fails", "uz": "imtihondan yiqiladi, yiqiladi", "lesson": 9, "book": 2},
    {"id": 155, "ar": "يَتَأَخَّرُ", "trans": "yataakhru", "tj": "дер мекунад", "ru": "опаздывает", "en": "is late, arrives late", "uz": "kechikadi, kech qoladi", "lesson": 9, "book": 2},
    {"id": 156, "ar": "سَيَذْهَبُ", "trans": "sayadhhabu", "tj": "хоҳад рафт", "ru": "пойдёт (буд. вр.)", "en": "will go (future tense)", "uz": "boradi (kelasi zamon)", "lesson": 9, "book": 2},
    {"id": 157, "ar": "سَيَرْجِعُ", "trans": "sayraji'u", "tj": "холо бар мегардад", "ru": "скоро вернётся", "en": "will return soon, will come back soon", "uz": "tez orada qaytadi", "lesson": 9, "book": 2},
    {"id": 158, "ar": "سَنَذْهَبُ", "trans": "sanadhhabu", "tj": "хоҳем рафт", "ru": "мы пойдём", "en": "we will go", "uz": "boramiz", "lesson": 9, "book": 2},
    {"id": 159, "ar": "سَوْفَ", "trans": "sawfa", "tj": "дар оянда (пешоянд)", "ru": "будет (маркер будущего)", "en": "will (future marker)", "uz": "boʻladi (kelasi zamon koʻrsatkichi)", "lesson": 9, "book": 2},
    {"id": 160, "ar": "لَنْ يَذْهَبَ", "trans": "yadhhabaan", "tj": "намеравад рафт (ҳаргиз)", "ru": "никогда не пойдёт", "en": "will never go", "uz": "hech qachon bormaydi", "lesson": 9, "book": 2},
    {"id": 161, "ar": "لَنْ تَذْهَبَ", "trans": "tadhhabaan", "tj": "намеравад рафт (ж)", "ru": "никогда не пойдёт (ж)", "en": "will never go (f)", "uz": "hech qachon bormaydi (ayol)", "lesson": 10, "book": 2},
    {"id": 162, "ar": "لَمْ يَذْهَبْ", "trans": "yadhhabam", "tj": "нарафт (гузашта)", "ru": "не ходил (прош. отриц.)", "en": "did not go (past negative)", "uz": "bormadi (oʻtgan zamon inkori)", "lesson": 10, "book": 2},
    {"id": 163, "ar": "لَمْ تَذْهَبْ", "trans": "tadhhabam", "tj": "нарафт (ж)", "ru": "не ходила", "en": "she did not go, did not go (f)", "uz": "bormadi (ayol)", "lesson": 10, "book": 2},
    {"id": 164, "ar": "لَمَّا", "trans": "lam-maa", "tj": "ҳанӯз... нашуда", "ru": "ещё не...", "en": "not yet", "uz": "hali emas, hali yoʻq", "lesson": 10, "book": 2},
    {"id": 165, "ar": "مَا ذَهَبَ", "trans": "dhahabama", "tj": "нарафт (такид)", "ru": "не ходил (усил.)", "en": "did not go (emphatic)", "uz": "bormadi (taʼkid bilan)", "lesson": 10, "book": 2},
    {"id": 166, "ar": "لاَ يَذْهَبُ", "trans": "yadhhabulaa", "tj": "намеравад рафт", "ru": "не идёт, не ходит", "en": "does not go, is not going", "uz": "bormaydi, bormayapti", "lesson": 10, "book": 2},
    {"id": 167, "ar": "أَنْ أَرَادَ", "trans": "aanaaraada", "tj": "хост ки", "ru": "захотел чтобы", "en": "wanted to, wanted that", "uz": "xohladi ki", "lesson": 10, "book": 2},
    {"id": 168, "ar": "أَنْ يُرِيدُ", "trans": "aanyuriydu", "tj": "мехоҳад ки", "ru": "хочет чтобы", "en": "wants to, wants that", "uz": "xohlaydi ki", "lesson": 10, "book": 2},
    {"id": 169, "ar": "أَنْ يُمْكِنُ", "trans": "aanyumkinu", "tj": "мумкин аст ки", "ru": "можно чтобы", "en": "it is possible to, it is possible that", "uz": "mumkin ki", "lesson": 10, "book": 2},
    {"id": 170, "ar": "أَنْ يَجِبُ", "trans": "aanyajibu", "tj": "лозим аст ки", "ru": "нужно чтобы", "en": "it is necessary to, it is necessary that", "uz": "kerak ki, lozim ki", "lesson": 10, "book": 2},
    {"id": 171, "ar": "أَنْ يُحِبُّ", "trans": "aanyuhibu", "tj": "дӯст медорад ки", "ru": "любит чтобы", "en": "likes to, likes that", "uz": "yaxshi koʻradi ki, sevadi ki", "lesson": 11, "book": 2},
    {"id": 172, "ar": "يَكَادُ", "trans": "ya-kaa-du", "tj": "наздик аст ки", "ru": "почти, едва", "en": "almost, barely", "uz": "deyarli, arang, zoʻrgʻa", "lesson": 11, "book": 2},
    {"id": 173, "ar": "أَنْ قَرَّرَ", "trans": "aanqarra", "tj": "тасмим гирифт ки", "ru": "решил чтобы", "en": "decided to, decided that", "uz": "qaror qildi ki", "lesson": 11, "book": 2},
    {"id": 174, "ar": "حَاوَلَ", "trans": "haa-wa-la", "tj": "кӯшиш кард ки", "ru": "попытался чтобы", "en": "tried to, attempted to", "uz": "urinib koʻrdi, harakat qildi", "lesson": 11, "book": 2},
    {"id": 175, "ar": "أَنْ يَفْهَمَ", "trans": "iyafhama", "tj": "то инки вай бифахмад", "ru": "чтобы он понял", "en": "so that he understands, that he may understand", "uz": "u tushunishi uchun, u tushunsin deb", "lesson": 11, "book": 2},
    {"id": 176, "ar": "أَنْ تَفْهَمَ", "trans": "itafhama", "tj": "то инки ту бифахми!", "ru": "чтобы ты понял", "en": "so that you understand, that you may understand", "uz": "sen tushunishing uchun", "lesson": 11, "book": 2},
    {"id": 177, "ar": "أَنْ نَفْهَمَ", "trans": "inafhama", "tj": "то инки мо бифахмем!", "ru": "чтобы мы поняли", "en": "so that we understand, that we may understand", "uz": "biz tushunishimiz uchun, biz tushunaylik deb", "lesson": 11, "book": 2},
    {"id": 178, "ar": "أَنْ أَفْهَمَ", "trans": "laiafhama", "tj": "То инки ман бифахмам!", "ru": "чтобы я понял", "en": "so that I understand, that I may understand", "uz": "men tushunishim uchun, men tushunay deb", "lesson": 11, "book": 2},
    {"id": 179, "ar": "لِأَنَّ", "trans": "li-an-na", "tj": "зеро ки, барои он ки", "ru": "потому что", "en": "because, since", "uz": "chunki, zero", "lesson": 11, "book": 2},
    {"id": 180, "ar": "لِكَيْ", "trans": "li-kay", "tj": "то ки", "ru": "чтобы, для того чтобы", "en": "in order to, so that", "uz": "uchun, toki", "lesson": 11, "book": 2},
    {"id": 181, "ar": "كَيْ", "trans": "kay", "tj": "то, барои ин ки", "ru": "чтобы", "en": "so that, in order to", "uz": "toki, uchun", "lesson": 12, "book": 2},
    {"id": 182, "ar": "لِأَجْلِ", "trans": "li-aj-li", "tj": "барои, ба хотири", "ru": "ради, для", "en": "for the sake of, for", "uz": "uchun, yoʻlida", "lesson": 12, "book": 2},
    {"id": 183, "ar": "كِتَابُهُ", "trans": "ki-taa-bu-hu", "tj": "китоби ӯ (м)", "ru": "его книга", "en": "his book", "uz": "uning kitobi (erkak)", "lesson": 12, "book": 2},
    {"id": 184, "ar": "كِتَابُهَا", "trans": "ki-taa-bu-haa", "tj": "китоби ӯ (ж)", "ru": "её книга", "en": "her book", "uz": "uning kitobi (ayol)", "lesson": 12, "book": 2},
    {"id": 185, "ar": "كِتَابُكَ", "trans": "ki-taa-bu-ka", "tj": "китоби ту (м)", "ru": "твоя книга", "en": "your book (m)", "uz": "sening kitobing (erkak)", "lesson": 12, "book": 2},
    {"id": 186, "ar": "كِتَابُكِ", "trans": "ki-taa-bu-ki", "tj": "китоби ту (ж)", "ru": "твоя книга (ж)", "en": "your book (f)", "uz": "sening kitobing (ayol)", "lesson": 12, "book": 2},
    {"id": 187, "ar": "كِتَابُكُمْ", "trans": "ki-taa-bu-kum", "tj": "китоби шумо", "ru": "ваша книга", "en": "your book (pl.)", "uz": "sizlarning kitobingiz, sizning kitobingiz", "lesson": 12, "book": 2},
    {"id": 188, "ar": "كِتَابُنَا", "trans": "ki-taa-bu-naa", "tj": "китоби мо", "ru": "наша книга", "en": "our book", "uz": "bizning kitobimiz", "lesson": 12, "book": 2},
    {"id": 189, "ar": "كِتَابُهُمْ", "trans": "ki-taa-bu-hum", "tj": "китоби онҳо", "ru": "их книга", "en": "their book", "uz": "ularning kitobi", "lesson": 12, "book": 2},
    {"id": 190, "ar": "ضَرَبَهُ", "trans": "darabahu", "tj": "ӯро зад", "ru": "ударил его", "en": "hit him, struck him", "uz": "uni urdi (erkak)", "lesson": 12, "book": 2},
    {"id": 191, "ar": "ضَرَبَهَا", "trans": "darabaha", "tj": "ӯро зад (ж)", "ru": "ударил её", "en": "hit her, struck her", "uz": "uni urdi (ayol)", "lesson": 13, "book": 2},
    {"id": 192, "ar": "سَأَلَهُ", "trans": "sa-a-la-hu", "tj": "аз ӯ пурсид", "ru": "спросил его", "en": "asked him", "uz": "undan soʻradi (erkak)", "lesson": 13, "book": 2},
    {"id": 193, "ar": "فَتَحَهُ", "trans": "fatahahu", "tj": "онро кушод", "ru": "открыл его", "en": "opened it (m)", "uz": "uni ochdi (erkak)", "lesson": 13, "book": 2},
    {"id": 194, "ar": "فَتَحَهَا", "trans": "fatahaha", "tj": "онро кушод (ж)", "ru": "открыл её", "en": "opened it (f)", "uz": "uni ochdi (ayol)", "lesson": 13, "book": 2},
    {"id": 195, "ar": "ذَكِيٌّ", "trans": "dhakiyun", "tj": "зирак, ҳушёр, заковатманд", "ru": "умный, сообразительный", "en": "smart, quick-witted", "uz": "aqlli, zehnli", "lesson": 13, "book": 2},
    {"id": 196, "ar": "غَبِيٌّ", "trans": "gha-biy-yun", "tj": "нодон, аҳмақ", "ru": "глупый", "en": "stupid, foolish", "uz": "ahmoq, nodon", "lesson": 13, "book": 2},
    {"id": 197, "ar": "أَخْلاَقٌ", "trans": "aakhlaaqun", "tj": "хулқ, кирдор, сират", "ru": "нравы, мораль", "en": "morals, manners", "uz": "axloq, odob", "lesson": 13, "book": 2},
    {"id": 198, "ar": "مَهْجَعٌ", "trans": "mahja'un", "tj": "хобгоҳ", "ru": "общежитие, спальня", "en": "dormitory, bedroom", "uz": "yotoqxona, yotoq xonasi", "lesson": 13, "book": 2},
    {"id": 199, "ar": "مَهَاجِعُ", "trans": "ma-haa-ji-'u", "tj": "хобгоҳҳо", "ru": "общежития", "en": "dormitories, bedrooms", "uz": "yotoqxonalar, yotoq xonalari", "lesson": 13, "book": 2},
    {"id": 200, "ar": "كَوْكَبٌ", "trans": "kawkabun", "tj": "ситора, сайёра", "ru": "звезда, планета", "en": "star, planet", "uz": "yulduz, sayyora", "lesson": 13, "book": 2},
    {"id": 201, "ar": "كَوَاكِبُ", "trans": "kawaakibu", "tj": "сайёраҳо", "ru": "звёзды, планеты", "en": "stars, planets", "uz": "yulduzlar, sayyoralar", "lesson": 14, "book": 2},
    {"id": 202, "ar": "فَرِيقٌ", "trans": "fariyqun", "tj": "қисм, гурӯҳ, тоифа", "ru": "команда, группа", "en": "team, group", "uz": "jamoa, guruh", "lesson": 14, "book": 2},
    {"id": 203, "ar": "فُرَقَاءُ", "trans": "fu-ra-qaa-u", "tj": "гурӯҳҳо", "ru": "группы, команды", "en": "groups, teams", "uz": "guruhlar, jamoalar", "lesson": 14, "book": 2},
    {"id": 204, "ar": "شَقِيقٌ", "trans": "shaqiyqun", "tj": "айни, ҳамхун", "ru": "родной брат", "en": "full brother, real brother", "uz": "tugʻishgan birodar, birodar", "lesson": 14, "book": 2},
    {"id": 205, "ar": "ثَمَنٌ", "trans": "thamanun", "tj": "нарх, қимат", "ru": "цена, стоимость", "en": "price, cost", "uz": "narx, qiymat", "lesson": 14, "book": 2},
    {"id": 206, "ar": "ثَمِينٌ", "trans": "thamiynun", "tj": "қиммат", "ru": "ценный, дорогой", "en": "valuable, expensive", "uz": "qimmatli, qimmat", "lesson": 14, "book": 2},
    {"id": 207, "ar": "عَالِمٌ", "trans": "'aa-li-mun", "tj": "олим, донишманд", "ru": "учёный", "en": "scholar, scientist", "uz": "olim", "lesson": 14, "book": 2},
    {"id": 208, "ar": "شَهِيرٌ", "trans": "shahiyrun", "tj": "машҳур, номдор", "ru": "знаменитый", "en": "famous, well-known", "uz": "mashhur, taniqli", "lesson": 14, "book": 2},
    {"id": 209, "ar": "مُعْجَمٌ", "trans": "mu'jamun", "tj": "луғат", "ru": "словарь", "en": "dictionary", "uz": "lugʻat", "lesson": 14, "book": 2},
    {"id": 210, "ar": "مَعَاجِمُ", "trans": "ma-'aa-ji-mu", "tj": "луғатҳо", "ru": "словари", "en": "dictionaries", "uz": "lugʻatlar", "lesson": 14, "book": 2},
    {"id": 211, "ar": "دُولاَرٌ", "trans": "duwlaarun", "tj": "доллар", "ru": "доллар", "en": "dollar", "uz": "dollar", "lesson": 15, "book": 2},
    {"id": 212, "ar": "رُوبِيَّةٌ", "trans": "ruwbiyhun", "tj": "рупия", "ru": "рупия", "en": "rupee", "uz": "rupiya", "lesson": 15, "book": 2},
    {"id": 213, "ar": "وَاسِعٌ", "trans": "waasi'un", "tj": "васеъ, фарох", "ru": "широкий, просторный", "en": "wide, spacious", "uz": "keng", "lesson": 15, "book": 2},
    {"id": 214, "ar": "ضَيِّقٌ", "trans": "dayiqun", "tj": "танг", "ru": "тесный, узкий", "en": "narrow, tight", "uz": "tor, ensiz", "lesson": 15, "book": 2},
    {"id": 215, "ar": "عِنَبٌ", "trans": "'inabun", "tj": "ангур", "ru": "виноград", "en": "grapes, grape", "uz": "uzum", "lesson": 15, "book": 2},
    {"id": 216, "ar": "تِينٌ", "trans": "tiynun", "tj": "анҷир", "ru": "инжир", "en": "fig, figs", "uz": "anjir", "lesson": 15, "book": 2},
    {"id": 217, "ar": "مَوْزٌ", "trans": "mawzun", "tj": "банан", "ru": "банан", "en": "banana", "uz": "banan", "lesson": 15, "book": 2},
    {"id": 218, "ar": "تُفَّاحٌ", "trans": "tuf-faa-hun", "tj": "себ", "ru": "яблоко", "en": "apple", "uz": "olma", "lesson": 15, "book": 2},
    {"id": 219, "ar": "جَوَابٌ", "trans": "jawaabun", "tj": "ҷавоб", "ru": "ответ", "en": "answer, reply", "uz": "javob", "lesson": 15, "book": 2},
    {"id": 220, "ar": "أَجْوِبَةٌ", "trans": "aajwibahun", "tj": "ҷавобҳо", "ru": "ответы", "en": "answers, replies", "uz": "javoblar", "lesson": 15, "book": 2},
    {"id": 221, "ar": "حَيَّةٌ", "trans": "hay-ya-tun", "tj": "мор", "ru": "змея", "en": "snake", "uz": "ilon", "lesson": 16, "book": 2},
    {"id": 222, "ar": "حَيَوَاتٌ", "trans": "hayawaatun", "tj": "морҳо", "ru": "змеи", "en": "snakes", "uz": "ilonlar", "lesson": 16, "book": 2},
    {"id": 223, "ar": "بَقَّالٌ", "trans": "baq-qaa-lun", "tj": "озуқафурӯш", "ru": "бакалейщик, продавец", "en": "grocer, seller", "uz": "baqqol, sotuvchi", "lesson": 16, "book": 2},
    {"id": 224, "ar": "فَهِمَ", "trans": "fahima", "tj": "вай мард фахмид (замони гузашта)", "ru": "понял", "en": "understood", "uz": "tushundi", "lesson": 16, "book": 2},
    {"id": 225, "ar": "شَرِبَ", "trans": "shariba", "tj": "вай мард нӯшид (замони гузашта)", "ru": "выпил", "en": "drank", "uz": "ichdi", "lesson": 16, "book": 2},
    {"id": 226, "ar": "مَصْنَعٌ", "trans": "masna'un", "tj": "корхона", "ru": "завод, фабрика", "en": "factory, plant", "uz": "zavod, fabrika", "lesson": 16, "book": 2},
    {"id": 227, "ar": "مَصَانِعُ", "trans": "ma-saa-ni-'u", "tj": "корхонаҳо", "ru": "заводы", "en": "factories, plants", "uz": "zavodlar, fabrikalar", "lesson": 16, "book": 2},
    {"id": 228, "ar": "عَامِلٌ", "trans": "'aa-mi-lun", "tj": "коркун", "ru": "рабочий", "en": "worker, laborer", "uz": "ishchi", "lesson": 16, "book": 2},
    {"id": 229, "ar": "مُهَنْدِسٌ", "trans": "muhandisun", "tj": "муҳандис", "ru": "инженер", "en": "engineer", "uz": "muhandis", "lesson": 16, "book": 2},
    {"id": 230, "ar": "مَحَطَّةٌ", "trans": "mahathun", "tj": "истгоҳ, вокзал", "ru": "станция, остановка", "en": "station, stop", "uz": "bekat, stansiya", "lesson": 16, "book": 2},
    {"id": 231, "ar": "أُجْرَةٌ", "trans": "aujrahun", "tj": "кироя", "ru": "плата, такси", "en": "fare, fee, taxi", "uz": "kira, toʻlov, taksi", "lesson": 17, "book": 2},
    {"id": 232, "ar": "مُتْحَفٌ", "trans": "mutahafun", "tj": "осорхона", "ru": "музей", "en": "museum", "uz": "muzey", "lesson": 17, "book": 2},
    {"id": 233, "ar": "مَجَلَّاتٌ", "trans": "majalatun", "tj": "маҷаллаҳо", "ru": "журналы", "en": "magazines, journals", "uz": "jurnallar", "lesson": 17, "book": 2},
    {"id": 234, "ar": "رَاكِبٌ", "trans": "raakibun", "tj": "савора, мусофир", "ru": "пассажир", "en": "passenger, rider", "uz": "yoʻlovchi", "lesson": 17, "book": 2},
    {"id": 235, "ar": "رُكَّابٌ", "trans": "ruk-kaa-bun", "tj": "савораҳо", "ru": "пассажиры", "en": "passengers, riders", "uz": "yoʻlovchilar", "lesson": 17, "book": 2},
    {"id": 236, "ar": "عِمَارَةٌ", "trans": "'i-maa-ra-tun", "tj": "бинои бисёрошёна", "ru": "здание, многоэтажка", "en": "building, high-rise", "uz": "bino, koʻp qavatli uy", "lesson": 17, "book": 2},
    {"id": 237, "ar": "عَمَائِرُ", "trans": "'a-maa-i-ru", "tj": "биноҳо", "ru": "здания", "en": "buildings", "uz": "binolar", "lesson": 17, "book": 2},
    {"id": 238, "ar": "سُورَةٌ", "trans": "suwrahun", "tj": "Сура (боб ё фасли) Қуръон", "ru": "сура (глава Корана)", "en": "surah (chapter of the Quran)", "uz": "sura (Qurʼon bobi)", "lesson": 17, "book": 2},
    {"id": 239, "ar": "سُوَرٌ", "trans": "su-wa-run", "tj": "сураҳо", "ru": "суры", "en": "surahs", "uz": "suralar", "lesson": 17, "book": 2},
    {"id": 240, "ar": "كَلِمَاتٌ", "trans": "ka-li-maa-tun", "tj": "калимаҳо", "ru": "слова", "en": "words", "uz": "soʻzlar", "lesson": 17, "book": 2},
    {"id": 241, "ar": "جُمَلٌ", "trans": "ju-ma-lun", "tj": "ҷумлаҳо", "ru": "предложения", "en": "sentences", "uz": "gaplar, jumlalar", "lesson": 18, "book": 2},
    {"id": 242, "ar": "مِشْطٌ", "trans": "mish-tun", "tj": "шона", "ru": "расчёска", "en": "comb", "uz": "taroq", "lesson": 18, "book": 2},
    {"id": 243, "ar": "مِخَدَّةٌ", "trans": "mikhadhun", "tj": "тагсарӣ", "ru": "подушка", "en": "pillow, cushion", "uz": "yostiq", "lesson": 18, "book": 2},
    {"id": 244, "ar": "مَقْعَدٌ", "trans": "maq'adun", "tj": "ҷои нишаст", "ru": "сиденье, место", "en": "seat, place", "uz": "oʻrindiq, joy", "lesson": 18, "book": 2},
    {"id": 245, "ar": "مَقَاعِدُ", "trans": "ma-qaa-'i-du", "tj": "ҷои нишастҳо", "ru": "сиденья, места", "en": "seats, places", "uz": "oʻrindiqlar, joylar", "lesson": 18, "book": 2},
    {"id": 246, "ar": "اِجْتِمَاعٌ", "trans": "ij-ti-maa-'un", "tj": "ҷамъомад", "ru": "встреча, собрание", "en": "meeting, gathering", "uz": "uchrashuv, yigʻilish", "lesson": 18, "book": 2},
    {"id": 247, "ar": "قِصَّةٌ", "trans": "qis-sa-tun", "tj": "қисса, ҳикоят", "ru": "рассказ, история", "en": "story, tale", "uz": "hikoya, qissa", "lesson": 18, "book": 2},
    {"id": 248, "ar": "قِصَصٌ", "trans": "qi-sa-sun", "tj": "қиссаҳо", "ru": "рассказы", "en": "stories, tales", "uz": "hikoyalar, qissalar", "lesson": 18, "book": 2},
    {"id": 249, "ar": "نَبِيٌّ", "trans": "na-biy-yun", "tj": "Набий, Паёмбар", "ru": "пророк", "en": "prophet", "uz": "paygʻambar, nabiy", "lesson": 18, "book": 2},
    {"id": 250, "ar": "جَائِزَةٌ", "trans": "jaa-i-za-tun", "tj": "мукофот, ҷоиза", "ru": "приз, награда", "en": "prize, award", "uz": "sovrin, mukofot", "lesson": 18, "book": 2},
    {"id": 251, "ar": "جَوَائِزُ", "trans": "jawaaiizu", "tj": "мукофотҳо", "ru": "призы, награды", "en": "prizes, awards", "uz": "sovrinlar, mukofotlar", "lesson": 19, "book": 2},
    {"id": 252, "ar": "قَاعَةٌ", "trans": "qaa-'a-tun", "tj": "зал", "ru": "зал, аудитория", "en": "hall, auditorium", "uz": "zal, auditoriya", "lesson": 19, "book": 2},
    {"id": 253, "ar": "ثَانِيَةٌ", "trans": "thaa-ni-ya-tun", "tj": "сония", "ru": "секунда", "en": "second", "uz": "soniya", "lesson": 19, "book": 2},
    {"id": 254, "ar": "دَقِيقَةٌ", "trans": "daqiyqahun", "tj": "дақиқа", "ru": "минута", "en": "minute", "uz": "daqiqa", "lesson": 19, "book": 2},
    {"id": 255, "ar": "لاَعِبٌ", "trans": "laa'ibun", "tj": "варзишгар", "ru": "игрок, спортсмен", "en": "player, athlete", "uz": "oʻyinchi, sportchi", "lesson": 19, "book": 2},
    {"id": 256, "ar": "لاَعِبُونَ", "trans": "laa'ibuwna", "tj": "варзишгарон", "ru": "игроки", "en": "players", "uz": "oʻyinchilar", "lesson": 19, "book": 2},
    {"id": 257, "ar": "نَجَحَ", "trans": "na-ja-ha", "tj": "наҷот ёфтан", "ru": "преуспел, сдал", "en": "succeeded, passed", "uz": "muvaffaq boʻldi, imtihondan oʻtdi", "lesson": 19, "book": 2},
    {"id": 258, "ar": "رَسَبَ", "trans": "ra-sa-ba", "tj": "нагузаштан, таҳнишин шудан", "ru": "провалился", "en": "failed", "uz": "imtihondan yiqildi, oʻtolmadi", "lesson": 19, "book": 2},
    {"id": 259, "ar": "بَرِيدٌ", "trans": "bariydun", "tj": "почта", "ru": "почта", "en": "mail, post", "uz": "pochta", "lesson": 19, "book": 2},
    {"id": 260, "ar": "إِذَاعَةٌ", "trans": "iidhaa'ahun", "tj": "паҳн кардан, радио", "ru": "радио", "en": "radio, broadcasting", "uz": "radio, eshittirish", "lesson": 19, "book": 2},
    {"id": 261, "ar": "تِلْفَازٌ", "trans": "til-faa-zun", "tj": "телевизор", "ru": "телевизор", "en": "television, TV", "uz": "televizor", "lesson": 20, "book": 2},
    {"id": 262, "ar": "الْأَزْهَرُ", "trans": "alaazharu", "tj": "Ал-Азҳар (донишгоҳ)", "ru": "Аль-Азхар (университет)", "en": "Al-Azhar (university)", "uz": "Al-Azhar (universitet)", "lesson": 20, "book": 2},
    {"id": 263, "ar": "وَجَدَ", "trans": "wa-ja-da", "tj": "пайдо кардан", "ru": "нашёл", "en": "found", "uz": "topdi", "lesson": 20, "book": 2},
    {"id": 264, "ar": "طَافَ", "trans": "taa-fa", "tj": "тавоф кардан", "ru": "совершил таваф", "en": "performed tawaf, circumambulated", "uz": "tavof qildi", "lesson": 20, "book": 2},
    {"id": 265, "ar": "حَجَّ", "trans": "haj-ja", "tj": "ҳаҷ кардан", "ru": "совершил хадж", "en": "performed hajj, went on pilgrimage", "uz": "haj qildi", "lesson": 20, "book": 2},
    {"id": 266, "ar": "شَفَى", "trans": "sha-faa", "tj": "шифо додан", "ru": "исцелил", "en": "healed, cured", "uz": "shifo berdi, sogʻaytirdi", "lesson": 20, "book": 2},
    {"id": 267, "ar": "رَضِيَ", "trans": "ra-di-ya", "tj": "розӣ шудан", "ru": "согласился, доволен", "en": "agreed, was pleased", "uz": "rozi boʻldi, mamnun boʻldi", "lesson": 20, "book": 2},
    {"id": 268, "ar": "شَكَا", "trans": "sha-kaa", "tj": "шикоят кардан", "ru": "пожаловался", "en": "complained", "uz": "shikoyat qildi", "lesson": 20, "book": 2},
    {"id": 269, "ar": "أُسْرَةٌ", "trans": "ausrahun", "tj": "оила, хонавода", "ru": "семья", "en": "family, household", "uz": "oila, xonadon", "lesson": 20, "book": 2},
    {"id": 270, "ar": "أُسَرٌ", "trans": "u-sa-run", "tj": "оилаҳо", "ru": "семьи", "en": "families, households", "uz": "oilalar, xonadonlar", "lesson": 20, "book": 2},
    {"id": 271, "ar": "إِخْوَانٌ", "trans": "iikhwaanun", "tj": "бародарони динӣ", "ru": "братья (по вере)", "en": "brothers (in faith)", "uz": "birodarlar (din boʻyicha)", "lesson": 21, "book": 2},
    {"id": 272, "ar": "صَوْمٌ", "trans": "saw-mun", "tj": "рӯза", "ru": "пост", "en": "fasting, fast", "uz": "roʻza", "lesson": 21, "book": 2},
    {"id": 273, "ar": "صِيَامٌ", "trans": "si-yaa-mun", "tj": "рӯзадорӣ", "ru": "держание поста", "en": "observing the fast, fasting", "uz": "roʻza tutish", "lesson": 21, "book": 2},
    {"id": 274, "ar": "جِهَاتٌ", "trans": "ji-haa-tun", "tj": "тарафҳо, ҷиҳатҳо", "ru": "стороны, районы", "en": "sides, regions", "uz": "tomonlar, hududlar", "lesson": 21, "book": 2},
    {"id": 275, "ar": "لُغَوِيٌّ", "trans": "lu-gha-wiy-yun", "tj": "луғавӣ, забонӣ", "ru": "языковой, лингвистический", "en": "linguistic, language-related", "uz": "tilga oid, lingvistik", "lesson": 21, "book": 2},
    {"id": 276, "ar": "تَلاَمِيذُ", "trans": "talaamiydhu", "tj": "талаба, хонанда", "ru": "ученики", "en": "pupils, students", "uz": "oʻquvchilar, shogirdlar", "lesson": 21, "book": 2},
    {"id": 277, "ar": "مُدِيرٌ", "trans": "mudiyrun", "tj": "мудир, директор", "ru": "директор, руководитель", "en": "director, manager", "uz": "direktor, rahbar", "lesson": 21, "book": 2},
    {"id": 278, "ar": "مُدِيرَةٌ", "trans": "mudiyrahun", "tj": "мудира", "ru": "директор (ж)", "en": "director (f)", "uz": "direktor (ayol)", "lesson": 21, "book": 2},
    {"id": 279, "ar": "شَرِيعَةٌ", "trans": "shariy'ahun", "tj": "шариат, шариъат", "ru": "шариат", "en": "sharia, Islamic law", "uz": "shariat", "lesson": 21, "book": 2},
    {"id": 280, "ar": "فِقْهٌ", "trans": "fiq-hun", "tj": "фиқҳ", "ru": "фикх", "en": "fiqh, Islamic jurisprudence", "uz": "fiqh", "lesson": 21, "book": 2},
    {"id": 281, "ar": "حَدِيثٌ", "trans": "hadiythun", "tj": "ҳадис", "ru": "хадис", "en": "hadith, tradition", "uz": "hadis", "lesson": 22, "book": 2},
    {"id": 282, "ar": "مَلاَئِكَةٌ", "trans": "malaaiikahun", "tj": "фариштаҳо", "ru": "ангелы", "en": "angels", "uz": "farishtalar, malaklar", "lesson": 22, "book": 2},
    {"id": 283, "ar": "طِينٌ", "trans": "tee-nun", "tj": "лой, гил, хок", "ru": "глина, грязь", "en": "clay, mud", "uz": "loy, gil", "lesson": 22, "book": 2},
    {"id": 284, "ar": "بَحْرٌ", "trans": "bah-run", "tj": "баҳр, дарё", "ru": "море", "en": "sea", "uz": "dengiz", "lesson": 22, "book": 2},
    {"id": 285, "ar": "بِحَارٌ", "trans": "bi-haa-run", "tj": "баҳрҳо", "ru": "моря", "en": "seas", "uz": "dengizlar", "lesson": 22, "book": 2},
    {"id": 286, "ar": "سَمَوَاتٌ", "trans": "samawaatun", "tj": "осмонҳо", "ru": "небеса", "en": "heavens, skies", "uz": "osmonlar, samolar", "lesson": 22, "book": 2},
    {"id": 287, "ar": "أَرْضٌ", "trans": "ar-dun", "tj": "замин", "ru": "земля", "en": "earth, land", "uz": "yer, zamin", "lesson": 22, "book": 2},
    {"id": 288, "ar": "شَمْسٌ", "trans": "sham-sun", "tj": "офтоб", "ru": "солнце", "en": "sun", "uz": "quyosh", "lesson": 22, "book": 2},
    {"id": 289, "ar": "نُورٌ", "trans": "noo-run", "tj": "нур, равшанӣ", "ru": "свет", "en": "light", "uz": "nur, yorugʻlik", "lesson": 22, "book": 2},
    {"id": 290, "ar": "أُسْبُوعٌ", "trans": "ausbuw'un", "tj": "ҳафта", "ru": "неделя", "en": "week", "uz": "hafta", "lesson": 22, "book": 2},
    {"id": 291, "ar": "شَهْرٌ", "trans": "shah-run", "tj": "моҳ", "ru": "месяц", "en": "month", "uz": "oy", "lesson": 23, "book": 2},
    {"id": 292, "ar": "الْمُقْبِلُ", "trans": "almuqbiu", "tj": "оянда", "ru": "следующий, будущий", "en": "next, coming", "uz": "keyingi, kelgusi", "lesson": 23, "book": 2},
    {"id": 293, "ar": "طِبٌّ", "trans": "tib-bun", "tj": "тибб", "ru": "медицина", "en": "medicine", "uz": "tibbiyot, tibb", "lesson": 23, "book": 2},
    {"id": 294, "ar": "هَنْدَسَةٌ", "trans": "handasahun", "tj": "ҳандаса", "ru": "инженерия", "en": "engineering", "uz": "muhandislik", "lesson": 23, "book": 2},
    {"id": 295, "ar": "عِلاَجٌ", "trans": "'ilaajun", "tj": "табобат, муолиҷа", "ru": "лечение", "en": "treatment, cure", "uz": "davolash, muolaja", "lesson": 23, "book": 2},
    {"id": 296, "ar": "دَوَاءٌ", "trans": "dawaa'un", "tj": "дору", "ru": "лекарство", "en": "medicine, drug", "uz": "dori", "lesson": 23, "book": 2},
    {"id": 297, "ar": "صَيْدَلِيَّةٌ", "trans": "saydaiyhun", "tj": "дорухона", "ru": "аптека", "en": "pharmacy, drugstore", "uz": "dorixona, apteka", "lesson": 23, "book": 2},

    # ── ТОМ 3 ──
    {"id": 298, "ar": "الْمَرْفُوعُ", "trans": "almarfuw'u", "tj": "марфуъ (ҳолати асосӣ)", "ru": "именительный падеж", "en": "nominative case, nominative", "uz": "bosh kelishik", "lesson": 1, "book": 3},
    {"id": 299, "ar": "الْمَنْصُوبُ", "trans": "almansuwbu", "tj": "мансуб (ҳолати насб)", "ru": "винительный падеж", "en": "accusative case, accusative", "uz": "tushum kelishigi", "lesson": 1, "book": 3},
    {"id": 300, "ar": "الْمَجْرُورُ", "trans": "almajruwru", "tj": "маҷрур (ҳолати ҷар)", "ru": "родительный падеж", "en": "genitive case, genitive", "uz": "qaratqich kelishigi", "lesson": 1, "book": 3},
    {"id": 301, "ar": "الضَّمَّةُ", "trans": "admhu", "tj": "зама", "ru": "огласовка дамма (у)", "en": "damma (vowel sign u)", "uz": "damma (u harakati)", "lesson": 1, "book": 3},
    {"id": 302, "ar": "الْفَتْحَةُ", "trans": "alfathahu", "tj": "фатҳа", "ru": "огласовка фатха (а)", "en": "fatha (vowel sign a)", "uz": "fatha (a harakati)", "lesson": 1, "book": 3},
    {"id": 303, "ar": "الْكَسْرَةُ", "trans": "alkasrahu", "tj": "касра", "ru": "огласовка касра (и)", "en": "kasra (vowel sign i)", "uz": "kasra (i harakati)", "lesson": 1, "book": 3},
    {"id": 304, "ar": "السُّكُونُ", "trans": "asukuwnu", "tj": "сукун (бе ҳаракат)", "ru": "сукун (отсутствие огласовки)", "en": "sukun (absence of a vowel)", "uz": "sukun (harakat yoʻqligi)", "lesson": 1, "book": 3},
    {"id": 305, "ar": "التَّنْوِينُ", "trans": "atnwiynu", "tj": "танвин (нунация)", "ru": "танвин (нунация)", "en": "tanwin (nunation)", "uz": "tanvin (nunatsiya)", "lesson": 1, "book": 3},
    {"id": 306, "ar": "الْفَتَى", "trans": "alfataa", "tj": "ҷавонписар", "ru": "юноша", "en": "young man, youth", "uz": "yigit, navqiron", "lesson": 1, "book": 3},
    {"id": 307, "ar": "الدَّاعِي", "trans": "ada'iy", "tj": "даъватгар", "ru": "призывающий", "en": "caller, inviter", "uz": "chaqiruvchi, daʼvat qiluvchi", "lesson": 1, "book": 3},
    {"id": 308, "ar": "الرَّاعِي", "trans": "ara'iy", "tj": "чӯпон, сарпараст", "ru": "пастух, опекун", "en": "shepherd, guardian", "uz": "choʻpon, vasiy", "lesson": 2, "book": 3},
    {"id": 309, "ar": "الْوَادِي", "trans": "alwaadiy", "tj": "водӣ, дарра", "ru": "долина, ущелье", "en": "valley, gorge", "uz": "vodiy, dara", "lesson": 2, "book": 3},
    {"id": 310, "ar": "الْمُرْتَضَى", "trans": "almartadaa", "tj": "писандида, розишуда", "ru": "одобренный", "en": "approved, accepted", "uz": "maʼqullangan, rozi boʻlingan", "lesson": 2, "book": 3},
    {"id": 311, "ar": "أَبُوكَ", "trans": "aabuwka", "tj": "падари ту", "ru": "твой отец", "en": "your father", "uz": "otang, sening otang", "lesson": 2, "book": 3},
    {"id": 312, "ar": "أَخُوكَ", "trans": "aakhuwka", "tj": "бародари ту", "ru": "твой брат", "en": "your brother", "uz": "birodaring, sening birodaring", "lesson": 2, "book": 3},
    {"id": 313, "ar": "حَمُوكَ", "trans": "hamuwka", "tj": "падарзулф, хусур", "ru": "свёкор/тесть", "en": "your father-in-law", "uz": "qaynotang, sening qaynotang", "lesson": 2, "book": 3},
    {"id": 314, "ar": "فُوكَ", "trans": "foo-ka", "tj": "даҳони ту", "ru": "твой рот", "en": "your mouth", "uz": "ogʻzing, sening ogʻzing", "lesson": 2, "book": 3},
    {"id": 315, "ar": "كُتِبَ", "trans": "ku-ti-ba", "tj": "навишта шуд", "ru": "было написано", "en": "was written", "uz": "yozildi", "lesson": 2, "book": 3},
    {"id": 316, "ar": "يُكْتَبُ", "trans": "yuktabu", "tj": "навишта мешавад", "ru": "пишется", "en": "is written", "uz": "yoziladi", "lesson": 2, "book": 3},
    {"id": 317, "ar": "ضُرِبَ", "trans": "du-ri-ba", "tj": "зада шуд", "ru": "был ударен", "en": "was hit, was struck", "uz": "urildi", "lesson": 2, "book": 3},
    {"id": 318, "ar": "يُضْرَبُ", "trans": "yudrabu", "tj": "зада мешавад", "ru": "ударяется", "en": "is hit, is struck", "uz": "uriladi", "lesson": 3, "book": 3},
    {"id": 319, "ar": "فُتِحَ", "trans": "fu-ti-ha", "tj": "кушода шуд", "ru": "было открыто", "en": "was opened", "uz": "ochildi", "lesson": 3, "book": 3},
    {"id": 320, "ar": "يُفْتَحُ", "trans": "yuftahu", "tj": "кушода мешавад", "ru": "открывается", "en": "is opened", "uz": "ochiladi", "lesson": 3, "book": 3},
    {"id": 321, "ar": "الْمَسْرُوقُ", "trans": "almasruwqu", "tj": "дуздидашуда", "ru": "украденное", "en": "stolen thing, stolen", "uz": "oʻgʻirlangan narsa, oʻgʻirlangan", "lesson": 3, "book": 3},
    {"id": 322, "ar": "الْمَذْبُوحُ", "trans": "almadhbuwhu", "tj": "забҳшуда", "ru": "зарезанный", "en": "slaughtered, slain", "uz": "soʻyilgan, boʻgʻizlangan", "lesson": 3, "book": 3},
    {"id": 323, "ar": "الْمَكْتُوبُ", "trans": "almaktuwbu", "tj": "навиштаи (хат)", "ru": "написанное, письмо", "en": "written, letter", "uz": "yozilgan, xat", "lesson": 3, "book": 3},
    {"id": 324, "ar": "الْمَجْهُولُ", "trans": "almajhuwlu", "tj": "маҷҳул, номаълум", "ru": "неизвестный", "en": "unknown, unidentified", "uz": "nomaʼlum, notanish", "lesson": 3, "book": 3},
    {"id": 325, "ar": "الْمَعْرُوفُ", "trans": "alma'ruwfu", "tj": "маълум, машҳур", "ru": "известный", "en": "known, well-known", "uz": "maʼlum, mashhur", "lesson": 3, "book": 3},
    {"id": 326, "ar": "الْمَسْمُوعُ", "trans": "almasmuw'u", "tj": "шунидашуда", "ru": "услышанное", "en": "heard, thing heard", "uz": "eshitilgan, eshitilgan narsa", "lesson": 3, "book": 3},
    {"id": 327, "ar": "الْمَفْصُولُ", "trans": "almafsuwlu", "tj": "ҷудошуда", "ru": "отделённый", "en": "separated, detached", "uz": "ajratilgan, alohida qilingan", "lesson": 3, "book": 3},
    {"id": 328, "ar": "النَّعْتُ", "trans": "an'tu", "tj": "сифат (тавсиф)", "ru": "определение (прилагательное)", "en": "attribute, adjective", "uz": "aniqlovchi, sifat", "lesson": 4, "book": 3},
    {"id": 329, "ar": "الْمَنْعُوتُ", "trans": "alman'uwtu", "tj": "мавсуф (исм)", "ru": "определяемое слово", "en": "modified word, described noun", "uz": "aniqlanmish, aniqlanuvchi soʻz", "lesson": 4, "book": 3},
    {"id": 330, "ar": "التَّوْكِيدُ", "trans": "atwkiydu", "tj": "таъкид", "ru": "усиление, подтверждение", "en": "emphasis, confirmation", "uz": "taʼkid, tasdiq", "lesson": 4, "book": 3},
    {"id": 331, "ar": "نَفْسُهُ", "trans": "nafsuhu", "tj": "худаш", "ru": "он сам", "en": "he himself, himself", "uz": "u oʻzi, oʻzi", "lesson": 4, "book": 3},
    {"id": 332, "ar": "عَيْنُهُ", "trans": "'aynuhu", "tj": "айнан худаш", "ru": "именно он сам", "en": "he himself exactly, the very same one", "uz": "aynan u oʻzi, oʻsha oʻzi", "lesson": 4, "book": 3},
    {"id": 333, "ar": "الْعَطْفُ", "trans": "al'atfu", "tj": "атф (пайвастшавӣ)", "ru": "сочинение, связь", "en": "coordination, connection, conjunction", "uz": "teng bogʻlanish, bogʻlanish", "lesson": 4, "book": 3},
    {"id": 334, "ar": "الْبَدَلُ", "trans": "albadalu", "tj": "бадал (ивазкунанда)", "ru": "аппозиция, замена", "en": "apposition, substitution, replacement", "uz": "badal, izohlovchi, almashtirish", "lesson": 4, "book": 3},
    {"id": 335, "ar": "لَدَيْكَ", "trans": "la-day-ka", "tj": "назди ту", "ru": "у тебя", "en": "with you, near you, you have", "uz": "senda, sening yoningda", "lesson": 4, "book": 3},
    {"id": 336, "ar": "لَدَيْهِ", "trans": "la-day-hi", "tj": "назди ӯ", "ru": "у него", "en": "with him, near him, he has", "uz": "unda, uning yonida", "lesson": 4, "book": 3},
    {"id": 337, "ar": "حَتَّى", "trans": "hat-taa", "tj": "то, ҳатто", "ru": "до, даже", "en": "until, up to, even", "uz": "gacha, hatto", "lesson": 4, "book": 3},
    {"id": 338, "ar": "رُبَّ", "trans": "rub-ba", "tj": "бисёре аз, баъзан", "ru": "сколько, много (руббa)", "en": "many a, often, sometimes", "uz": "koʻp, baʼzan", "lesson": 5, "book": 3},
    {"id": 339, "ar": "التَّمْيِيزُ", "trans": "atmyiyzu", "tj": "тамйиз (фарқкунанда)", "ru": "тамйиз (пояснение числа)", "en": "tamyiz, specification, explanation of number", "uz": "tamyiz, sonni izohlash", "lesson": 5, "book": 3},
    {"id": 340, "ar": "مُبَشِّراً", "trans": "mubashiraan", "tj": "хушхабар оваранда", "ru": "радостной вестью", "en": "bearer of glad tidings, bringing good news", "uz": "xushxabar keltiruvchi, xushxabar bilan", "lesson": 5, "book": 3},
    {"id": 341, "ar": "يَخْطُبُ", "trans": "yakhtubu", "tj": "хутба мехонад", "ru": "произносит хутбу", "en": "delivers a sermon, gives a sermon", "uz": "xutba oʻqiydi, xutba qiladi", "lesson": 5, "book": 3},
    {"id": 342, "ar": "مُبَكِّراً", "trans": "mubakiraan", "tj": "пагоҳӣ, барвақт", "ru": "ранним утром", "en": "early in the morning, early", "uz": "erta tongda, barvaqt", "lesson": 5, "book": 3},
    {"id": 343, "ar": "الظَّرْفُ", "trans": "azrfu", "tj": "зарф (мубин маъно)", "ru": "обстоятельство", "en": "adverbial, adverb", "uz": "hol, ravish, zarf", "lesson": 5, "book": 3},
    {"id": 344, "ar": "وَرَاءَ", "trans": "waraa'a", "tj": "пушти", "ru": "позади", "en": "behind", "uz": "orqasida, ortida", "lesson": 5, "book": 3},
    {"id": 345, "ar": "فَوْقَ", "trans": "faw-qa", "tj": "болои", "ru": "над", "en": "above, over", "uz": "ustida, tepasida", "lesson": 5, "book": 3},
    {"id": 346, "ar": "تَحْتَ", "trans": "tah-ta", "tj": "зери", "ru": "под", "en": "under, beneath", "uz": "ostida, tagida", "lesson": 5, "book": 3},
    {"id": 347, "ar": "مَرَّةً", "trans": "mar-ra-tan", "tj": "як бор", "ru": "один раз", "en": "once, one time", "uz": "bir marta, bir bor", "lesson": 5, "book": 3},
    {"id": 348, "ar": "مَرَّتَيْنِ", "trans": "martayni", "tj": "ду бор", "ru": "два раза", "en": "twice, two times", "uz": "ikki marta, ikki bor", "lesson": 6, "book": 3},
    {"id": 349, "ar": "بُكْرَةً", "trans": "bukrahan", "tj": "субҳи барвақт", "ru": "ранним утром", "en": "in the early morning, early morning", "uz": "erta tongda, ertalab", "lesson": 6, "book": 3},
    {"id": 350, "ar": "ثَمَّ", "trans": "tham-ma-ta", "tj": "дар он ҷо", "ru": "там (зарф)", "en": "there (adverb), there", "uz": "u yerda (ravish), oʻsha yerda", "lesson": 6, "book": 3},
    {"id": 351, "ar": "إِذَا", "trans": "i-dhaa", "tj": "вақте ки, агар", "ru": "когда, если", "en": "when, if", "uz": "qachon, agar", "lesson": 6, "book": 3},
    {"id": 352, "ar": "لَوْ", "trans": "law", "tj": "агар мебуд", "ru": "если бы (нереальное)", "en": "if (unreal)", "uz": "agar (xayoliy)", "lesson": 6, "book": 3},
    {"id": 353, "ar": "لَوْلَا", "trans": "law-laa", "tj": "агар набуд", "ru": "если бы не", "en": "if not for, were it not for", "uz": "agar boʻlmaganida, agar boʻlmasa edi", "lesson": 6, "book": 3},
    {"id": 354, "ar": "مَنْ", "trans": "man", "tj": "ҳар ки", "ru": "тот кто", "en": "the one who, whoever", "uz": "kimki, kim boʻlsa", "lesson": 6, "book": 3},
    {"id": 355, "ar": "إِنْ", "trans": "in", "tj": "агар (шарт)", "ru": "если (условие)", "en": "if (condition)", "uz": "agar (shart)", "lesson": 6, "book": 3},
    {"id": 356, "ar": "ثُمَّ", "trans": "thum-ma", "tj": "сипас, баъдан", "ru": "затем, потом", "en": "then, afterwards", "uz": "soʻng, keyin", "lesson": 6, "book": 3},
    {"id": 357, "ar": "أَوْ", "trans": "aw", "tj": "ё, ё ин ки", "ru": "или", "en": "or", "uz": "yoki", "lesson": 6, "book": 3},
    {"id": 358, "ar": "لَكِنْ", "trans": "laa-kin", "tj": "аммо", "ru": "однако", "en": "but, however", "uz": "lekin, ammo", "lesson": 7, "book": 3},
    {"id": 359, "ar": "أَمْ", "trans": "am", "tj": "ё (дар савол)", "ru": "или (в вопросе)", "en": "or (in questions)", "uz": "yoki (savolda)", "lesson": 7, "book": 3},
    {"id": 360, "ar": "لَا", "trans": "laa", "tj": "не, нест", "ru": "нет, не", "en": "no, not", "uz": "yoʻq, emas", "lesson": 7, "book": 3},
    {"id": 361, "ar": "اِسْمُ الآلَةِ", "trans": "alaaahiasmu", "tj": "исми олат (асбоб)", "ru": "имя орудия", "en": "noun of instrument, instrument noun", "uz": "asbob oti, qurol oti", "lesson": 7, "book": 3},
    {"id": 362, "ar": "مَضْرُوبٌ", "trans": "madruwbun", "tj": "задазадашуда", "ru": "побитый", "en": "beaten, struck", "uz": "urilgan, kaltaklangan", "lesson": 7, "book": 3},
    {"id": 363, "ar": "مِبْرَدٌ", "trans": "mibradun", "tj": "сӯҳан", "ru": "напильник", "en": "file, rasp", "uz": "egov", "lesson": 7, "book": 3},
    {"id": 364, "ar": "مِكْنَسَةٌ", "trans": "miknasahun", "tj": "ҷору", "ru": "метла", "en": "broom", "uz": "supurgi", "lesson": 7, "book": 3},
    {"id": 365, "ar": "مِقَصٌّ", "trans": "mi-qas-sun", "tj": "қайчӣ", "ru": "ножницы", "en": "scissors", "uz": "qaychi", "lesson": 7, "book": 3},
    {"id": 366, "ar": "مِسْطَرَةٌ", "trans": "mistarahun", "tj": "хаткаш", "ru": "линейка", "en": "ruler", "uz": "chizgʻich", "lesson": 7, "book": 3},
    {"id": 367, "ar": "مِحْجَنٌ", "trans": "mihjanun", "tj": "чӯби каҷ", "ru": "крюк, загнутая палка", "en": "hook, crooked stick", "uz": "ilgak, egri tayoq", "lesson": 7, "book": 3},
    {"id": 368, "ar": "الْمُضَعَّفُ", "trans": "almuda'fu", "tj": "музаъаф (феъли такрорӣ)", "ru": "удвоенный глагол", "en": "doubled verb, geminate verb", "uz": "ikkilangan fel, muzaʼaf fel", "lesson": 8, "book": 3},
    {"id": 369, "ar": "الْمَصْدَرُ", "trans": "almasdaru", "tj": "масдар", "ru": "масдар (отглагольное имя)", "en": "verbal noun, masdar", "uz": "masdar, harakat nomi", "lesson": 8, "book": 3},
    {"id": 370, "ar": "الْقِرَاءَةُ", "trans": "alqiraa'ahu", "tj": "хондан", "ru": "чтение", "en": "reading", "uz": "oʻqish", "lesson": 8, "book": 3},
    {"id": 371, "ar": "الصَّوْمُ", "trans": "aswmu", "tj": "рӯза", "ru": "пост", "en": "fasting, fast", "uz": "roʻza, roʻza tutish", "lesson": 8, "book": 3},
    {"id": 372, "ar": "الصَّلَاةُ", "trans": "aslaahu", "tj": "намоз", "ru": "молитва", "en": "prayer, salah", "uz": "namoz", "lesson": 8, "book": 3},
    {"id": 373, "ar": "التَّوْبَةُ", "trans": "atwbahu", "tj": "тавба", "ru": "покаяние", "en": "repentance, penitence", "uz": "tavba", "lesson": 8, "book": 3},
    {"id": 374, "ar": "الذِّكْرُ", "trans": "adhikru", "tj": "зикр", "ru": "поминание Аллаха", "en": "remembrance of Allah, dhikr", "uz": "Allohni yod etish, zikr", "lesson": 8, "book": 3},
    {"id": 375, "ar": "الصَّدَقَةُ", "trans": "asdaqahu", "tj": "садақа", "ru": "пожертвование", "en": "donation, charity, alms", "uz": "sadaqa, xayriya", "lesson": 8, "book": 3},
    {"id": 376, "ar": "قَطُّ", "trans": "qat-tu", "tj": "ҳаргиз (гузашта)", "ru": "никогда (прошедшее)", "en": "never (past)", "uz": "hech qachon (oʻtgan zamon)", "lesson": 8, "book": 3},
    {"id": 377, "ar": "أَبَدًا", "trans": "aabadaan", "tj": "ҳаргиз (оянда)", "ru": "никогда (будущее)", "en": "never (future)", "uz": "hech qachon (kelasi zamon)", "lesson": 8, "book": 3},
    {"id": 378, "ar": "لاَ يَزَالُ", "trans": "yazaalulaa", "tj": "ҳамоно ҳаст", "ru": "всё ещё есть", "en": "still is, still remains", "uz": "hali ham bor, hamon boʻlib turibdi", "lesson": 9, "book": 3},
    {"id": 379, "ar": "أَوْشَكَ أَنْ", "trans": "aanaawshaka", "tj": "қариб буд ки", "ru": "чуть не (был близок к)", "en": "almost, was about to, was close to", "uz": "deyarli, oz qoldi, yaqin boʻldi", "lesson": 9, "book": 3},
    {"id": 380, "ar": "قَدْ", "trans": "qad", "tj": "қад (тахкид)", "ru": "уже, ведь (усиление)", "en": "already, indeed (emphasis)", "uz": "allaqachon, axir (taʼkid)", "lesson": 9, "book": 3},
    {"id": 381, "ar": "لَوْ عَرَفْتَ", "trans": "'araftaaw", "tj": "агар медонистӣ", "ru": "если бы ты знал", "en": "if you knew, if you had known", "uz": "agar bilganingda, agar bilsang edi", "lesson": 9, "book": 3},
    {"id": 382, "ar": "كُنْتُ", "trans": "kun-tu", "tj": "будам", "ru": "я был", "en": "I was", "uz": "men edim, men boʻldim", "lesson": 9, "book": 3},
    {"id": 383, "ar": "لَبِثَ", "trans": "la-bi-tha", "tj": "монд, дер монд", "ru": "задержался, пробыл", "en": "lingered, stayed", "uz": "kechikdi, turib qoldi", "lesson": 9, "book": 3},
    {"id": 384, "ar": "ثَمَّ", "trans": "tham-ma-ta", "tj": "дар он ҷо", "ru": "там", "en": "there", "uz": "u yerda, oʻsha yerda", "lesson": 9, "book": 3},
    {"id": 385, "ar": "حَيْثُ", "trans": "hay-thu", "tj": "ҷое ки, зеро ки", "ru": "там где, потому что", "en": "where, because", "uz": "qayerda, chunki", "lesson": 9, "book": 3},
    {"id": 386, "ar": "إِذْ", "trans": "idh", "tj": "он вақт ки", "ru": "когда (прошедшее)", "en": "when (past)", "uz": "qachon (oʻtgan zamon), oʻshanda", "lesson": 9, "book": 3},
    {"id": 387, "ar": "هَذِهِ الْمَرَّةَ", "trans": "almarha", "tj": "ин дафъа", "ru": "в этот раз", "en": "this time", "uz": "bu safar, bu gal", "lesson": 9, "book": 3},
    {"id": 388, "ar": "مُنْذُ", "trans": "mun-dhu", "tj": "аз вақте ки, баъд аз", "ru": "с тех пор как, давно", "en": "since, for a long time", "uz": "-dan beri, anchadan beri, beri", "lesson": 10, "book": 3},
    {"id": 389, "ar": "مُذْ", "trans": "mudh", "tj": "аз (замон)", "ru": "с (указание времени)", "en": "from (time), since (time)", "uz": "-dan (vaqt), -dan beri (vaqt)", "lesson": 10, "book": 3},
    {"id": 390, "ar": "خِلَالَ", "trans": "khilaala", "tj": "дар давоми", "ru": "в течение", "en": "during, throughout", "uz": "davomida, mobaynida", "lesson": 10, "book": 3},
    {"id": 391, "ar": "بِسَبَبِ", "trans": "bisababi", "tj": "аз сабаби", "ru": "по причине", "en": "because of, due to", "uz": "sababli, tufayli", "lesson": 10, "book": 3},
    {"id": 392, "ar": "بِمَنْزِلَةِ", "trans": "bimanziahi", "tj": "дар дараҷаи", "ru": "в положении, наравне с", "en": "in the position of, on a par with", "uz": "oʻrnida, darajasida", "lesson": 10, "book": 3},
    {"id": 393, "ar": "الْمُرَاقِبُ", "trans": "almiraaqibu", "tj": "нозир", "ru": "надзиратель, наблюдатель", "en": "supervisor, observer", "uz": "nazoratchi, kuzatuvchi", "lesson": 10, "book": 3},
    {"id": 394, "ar": "الرُّكُوعُ", "trans": "arukuw'u", "tj": "рукуъ", "ru": "поясной поклон", "en": "bowing, ruku", "uz": "rukuʼ, belgacha egilish", "lesson": 10, "book": 3},
    {"id": 395, "ar": "السُّجُودُ", "trans": "asujuwdu", "tj": "саҷда", "ru": "земной поклон", "en": "prostration, sajdah", "uz": "sajda, yerga bosh qoʻyish", "lesson": 10, "book": 3},
    {"id": 396, "ar": "التَّسْبِيحُ", "trans": "atsbiyhu", "tj": "тасбеҳ (субҳоналлоҳ)", "ru": "тасбих (субханаллах)", "en": "tasbih, glorification of Allah", "uz": "tasbeh, Allohni ulugʻlash", "lesson": 10, "book": 3},
    {"id": 397, "ar": "الرُّكْنُ", "trans": "aruknu", "tj": "рукн (гӯшаи Каъба)", "ru": "угол Каабы", "en": "corner of the Kaaba, corner", "uz": "Kaʼba burchagi, burchak", "lesson": 10, "book": 3},
    {"id": 398, "ar": "الْمِنْبَرُ", "trans": "alminbrau", "tj": "минбар", "ru": "минбар (кафедра мечети)", "en": "minbar, mosque pulpit, pulpit", "uz": "minbar, masjid minbari", "lesson": 11, "book": 3},
    {"id": 399, "ar": "مُرَافَقَةٌ", "trans": "muraafaqahun", "tj": "ҳамроҳӣ", "ru": "сопровождение", "en": "accompaniment, companionship", "uz": "hamrohlik, kuzatib borish", "lesson": 11, "book": 3},
    {"id": 400, "ar": "السِّيرَةُ", "trans": "asiyrahu", "tj": "сира (зиндагинома)", "ru": "жизнеописание", "en": "biography, life story", "uz": "tarjimai hol, siyrat", "lesson": 11, "book": 3},
    {"id": 401, "ar": "الْفِقْهُ", "trans": "alfiqhu", "tj": "фиқҳ", "ru": "фикх", "en": "fiqh, Islamic jurisprudence", "uz": "fiqh, islom huquqshunosligi", "lesson": 11, "book": 3},
    {"id": 402, "ar": "الْمُقَرَّرُ", "trans": "almuqarru", "tj": "муқаррар, муайян", "ru": "установленное, утверждённое", "en": "established, approved", "uz": "belgilangan, tasdiqlangan", "lesson": 11, "book": 3},
    {"id": 403, "ar": "مَرَافِقُ", "trans": "maraafiqu", "tj": "утоқҳои ёрирасон", "ru": "вспомогательные помещения", "en": "auxiliary rooms, facilities", "uz": "yordamchi xonalar, qulayliklar", "lesson": 11, "book": 3},
    {"id": 404, "ar": "الْفُرْصَةُ", "trans": "alfursahu", "tj": "фурсат", "ru": "возможность, шанс", "en": "opportunity, chance", "uz": "imkoniyat, fursat", "lesson": 11, "book": 3},
    {"id": 405, "ar": "الرُّخْصَةُ", "trans": "arukhsahu", "tj": "рухсат", "ru": "разрешение, льгота", "en": "permission, concession, privilege", "uz": "ruxsat, imtiyoz", "lesson": 11, "book": 3},
    {"id": 406, "ar": "الْعَزِيمَةُ", "trans": "al'aziymahu", "tj": "азимат", "ru": "строгое требование", "en": "strict requirement, firm resolve", "uz": "qatʼiy talab, qatʼiyat", "lesson": 11, "book": 3},
]


# ─── ХЕЛПЕРЫ ──────────────────────────────────────────────────
_cache = {}


def get_lesson_words(lesson: int, book: int = 1) -> list:
    """Words for a specific lesson within a book."""
    key = (book, lesson)
    if key in _cache:
        return _cache[key]
    result = [w for w in WORDS if w["book"] == book and w["lesson"] == lesson]
    _cache[key] = result
    return result


def get_word_by_id(word_id: int) -> dict:
    return next((w for w in WORDS if w["id"] == word_id), None)


def get_words_by_ids(ids: list) -> list:
    id_set = set(ids)
    return [w for w in WORDS if w["id"] in id_set]


def get_book_words(book: int) -> list:
    return [w for w in WORDS if w["book"] == book]


def get_book_info(book: int) -> dict:
    return BOOKS_INFO.get(book, BOOKS_INFO[1])


def get_book_title(book: int, lang: str) -> str:
    info = get_book_info(book)
    return info.get(f"title_{lang}") or info["title_ru"]


def get_total_lessons(book: int) -> int:
    return BOOKS_INFO.get(book, {}).get("total_lessons", 7)


def get_label(word: dict, lang: str) -> str:
    """Translation in user lang, with ru fallback for empty en/uz."""
    val = word.get(lang)
    if val:
        return val
    return word.get("ru") or word.get("tj") or ""


def make_choices(correct: dict, all_words: list, lang: str) -> tuple:
    wrong_pool = [w for w in all_words if w["id"] != correct["id"]]
    wrong = random.sample(wrong_pool, min(3, len(wrong_pool)))
    choices = [correct] + wrong
    random.shuffle(choices)
    labels = [get_label(w, lang) for w in choices]
    return labels, get_label(correct, lang), [w["id"] for w in choices]


def normalize(text: str) -> str:
    return text.strip().lower()


_ARABIC_DIACRITICS = set("ًٌٍَُِّْـ")


def normalize_arabic(s: str) -> str:
    """Strip Arabic diacritics + whitespace for input comparison."""
    return ''.join(c for c in s if c not in _ARABIC_DIACRITICS).strip()


# ── Сравнение письменных ответов ──────────────────────────────
# Мягкая нормализация: регистр, ё/е, ударение, знаки препинания, дефисы,
# апострофы (узб. oʻ/gʻ печатают как o' / oʻ / o` — считаем одним и тем же).
# й, ӣ, ӯ НЕ трогаем — это разные буквы, иначе "мой"/"мои" совпадут.
_STRESS_MARKS = {chr(0x0300), chr(0x0301)}
_APOSTROPHES = "".join(chr(c) for c in (0x02BB, 0x02BC, 0x02B9, 0x02BD, 0x27, 0x60, 0xB4, 0x2018, 0x2019, 0x2032))
_APOS_RE = re.compile("[" + re.escape(_APOSTROPHES) + "]")
_PUNCT_RE = re.compile(r"[.!?:\"«»“”„()\[\]{}…\-–—_]")
_PAREN_RE = re.compile(r"\([^)]*\)|\[[^\]]*\]")


def _norm_answer(s: str) -> str:
    s = unicodedata.normalize("NFD", s or "")
    s = unicodedata.normalize("NFC", "".join(c for c in s if c not in _STRESS_MARKS))
    s = s.lower().replace("ё", "е")
    s = _APOS_RE.sub("", s)
    s = _PUNCT_RE.sub(" ", s)
    return " ".join(s.split())


def _split_top(val: str) -> list:
    """Split on , ; / but not inside (...) or [...]."""
    parts, buf, depth = [], [], 0
    for ch in val:
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth = max(0, depth - 1)
        if depth == 0 and ch in ",;/":
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    parts.append("".join(buf))
    return parts


def _variant_set(val: str) -> set:
    """Acceptable answers for one translation string: every comma-separated
    variant, both with and without its parenthetical hint — "врач (ж)" -> "врач"."""
    out = set()
    for part in _split_top(val):
        for cand in (part, _PAREN_RE.sub(" ", part)):
            n = _norm_answer(cand)
            if n:
                out.add(n)
    return out


def check_answer(answer: str, word: dict) -> bool:
    """Accept answer if it matches any translation variant in any language.

    Also accepts the whole displayed translation typed back ("ручка, карандаш")
    or several variants in any order — every typed part must be a valid variant.
    """
    typed = _norm_answer(answer)
    if not typed:
        return False
    typed_parts = {p for p in (_norm_answer(x) for x in _split_top(answer)) if p}
    for lang in ("ru", "tj", "en", "uz"):
        val = word.get(lang)
        if not val:
            continue
        variants = _variant_set(val)
        if typed in variants or (typed_parts and typed_parts <= variants):
            return True
    return False


def check_arabic_answer(answer: str, word: dict) -> bool:
    """Accept Arabic answer matching the word's Arabic form (diacritics ignored)."""
    return normalize_arabic(answer) == normalize_arabic(word["ar"])
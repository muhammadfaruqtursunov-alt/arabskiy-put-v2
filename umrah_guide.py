# -*- coding: utf-8 -*-
"""Разговорник для паломников Умры и Хаджа.
~100 фраз по 8 разделам: числа, аэропорт, такси, отель, рынок, кафе, мечеть, основные фразы.
Каждая фраза: ar, trans, ru, tj, en, uz.
"""

SECTIONS = {
    "greetings": {
        "emoji": "🤲",
        "title_ru": "Основные фразы", "title_tj": "Ибораҳои асосӣ", "title_en": "Basic phrases", "title_uz": "Asosiy iboralar",
        "phrases": [
            {"ar": "السَّلَامُ عَلَيْكُمْ",      "trans": "Ассаламу алайкум",        "ru": "Мир вам (приветствие)",              "tj": "Саломи шумо бошад (салом)",          "en": "Peace be upon you (greeting)",       "uz": "Sizga tinchlik (salomlashish)"},
            {"ar": "وَعَلَيْكُمُ السَّلَام",       "trans": "Ва алайкум ассалам",      "ru": "И вам мир (ответ)",                  "tj": "Ва ба шумо ҳам салом (ҷавоб)",       "en": "And peace be upon you (reply)",      "uz": "Va sizga ham tinchlik (javob)"},
            {"ar": "جَزَاكَ اللَّهُ خَيْرًا",      "trans": "Джазакаллаху хайран",     "ru": "Да воздаст тебе Аллах благом",      "tj": "Аллоҳ ба ту хайр диҳад",            "en": "May Allah reward you with good",     "uz": "Alloh sizga yaxshilik bersin"},
            {"ar": "شُكْرًا",                       "trans": "Шукран",                  "ru": "Спасибо",                            "tj": "Ташаккур",                           "en": "Thank you",                          "uz": "Rahmat"},
            {"ar": "عَفْوًا",                       "trans": "Афван",                   "ru": "Пожалуйста / Не за что",            "tj": "Марҳамат / Хоҳиш намекунам",        "en": "You're welcome / Excuse me",        "uz": "Marhamat / Arzimaydi"},
            {"ar": "مِنْ فَضْلِكَ",                "trans": "Мин фадлик",              "ru": "Пожалуйста (просьба)",              "tj": "Лутфан (хоҳиш)",                    "en": "Please (request)",                  "uz": "Iltimos (so'rov)"},
            {"ar": "نَعَمْ",                        "trans": "На'ам",                   "ru": "Да",                                 "tj": "Ҳа",                                 "en": "Yes",                               "uz": "Ha"},
            {"ar": "لَا",                           "trans": "Ля",                      "ru": "Нет",                                "tj": "Не",                                 "en": "No",                                "uz": "Yo'q"},
            {"ar": "لَا أُرِيدُ",                  "trans": "Ля уриду",                "ru": "Не хочу / Не надо",                 "tj": "Намехоҳам / Лозим нест",            "en": "I don't want / No need",            "uz": "Xohlamayman / Kerak emas"},
            {"ar": "بِكَمْ؟",                       "trans": "Бикам?",                  "ru": "Сколько?",                          "tj": "Чанд?",                              "en": "How much?",                         "uz": "Qancha?"},
            {"ar": "أَيْنَ؟",                       "trans": "Айна?",                   "ru": "Где?",                               "tj": "Куҷо?",                              "en": "Where?",                            "uz": "Qayerda?"},
            {"ar": "مَتَى؟",                        "trans": "Мата?",                   "ru": "Когда?",                             "tj": "Кай?",                               "en": "When?",                             "uz": "Qachon?"},
        ],
    },

    "numbers": {
        "emoji": "🔢",
        "title_ru": "Числа", "title_tj": "Рақамҳо", "title_en": "Numbers", "title_uz": "Raqamlar",
        "phrases": [
            {"ar": "وَاحِدٌ",    "trans": "вáхид",     "ru": "1",   "tj": "1",   "en": "1",   "uz": "1"},
            {"ar": "اثْنَانِ",   "trans": "иснéйн",    "ru": "2",   "tj": "2",   "en": "2",   "uz": "2"},
            {"ar": "ثَلَاثَةٌ",  "trans": "сала́са",   "ru": "3",   "tj": "3",   "en": "3",   "uz": "3"},
            {"ar": "أَرْبَعَةٌ", "trans": "árбаа",     "ru": "4",   "tj": "4",   "en": "4",   "uz": "4"},
            {"ar": "خَمْسَةٌ",   "trans": "хáмса",     "ru": "5",   "tj": "5",   "en": "5",   "uz": "5"},
            {"ar": "سِتَّةٌ",    "trans": "ситта",      "ru": "6",   "tj": "6",   "en": "6",   "uz": "6"},
            {"ar": "سَبْعَةٌ",   "trans": "сáбаа",     "ru": "7",   "tj": "7",   "en": "7",   "uz": "7"},
            {"ar": "ثَمَانِيَةٌ","trans": "самáния",   "ru": "8",   "tj": "8",   "en": "8",   "uz": "8"},
            {"ar": "تِسْعَةٌ",   "trans": "тис'а",     "ru": "9",   "tj": "9",   "en": "9",   "uz": "9"},
            {"ar": "عَشَرَةٌ",   "trans": "áшара",     "ru": "10",  "tj": "10",  "en": "10",  "uz": "10"},
            {"ar": "عِشْرُونَ",  "trans": "ишрун",      "ru": "20",  "tj": "20",  "en": "20",  "uz": "20"},
            {"ar": "خَمْسُونَ",  "trans": "хамсун",     "ru": "50",  "tj": "50",  "en": "50",  "uz": "50"},
            {"ar": "مِئَةٌ",     "trans": "мия",        "ru": "100", "tj": "100", "en": "100", "uz": "100"},
        ],
    },

    "airport": {
        "emoji": "✈️",
        "title_ru": "Аэропорт", "title_tj": "Фурудгоҳ", "title_en": "Airport", "title_uz": "Aeroport",
        "phrases": [
            {"ar": "أَيْنَ الْمِيقَاتُ؟",          "trans": "Айна-ль-Микат?",           "ru": "Где Микат? (место для ихрама)",       "tj": "Микот куҷост? (ҷои ихром)",          "en": "Where is the Miqat? (ihram place)",  "uz": "Miqot qayerda? (ihrom joyi)"},
            {"ar": "أَيْنَ الْجَوَازَاتُ؟",         "trans": "Айна-ль-джавазат?",        "ru": "Где паспортный контроль?",           "tj": "Назорати паспорт куҷост?",           "en": "Where is passport control?",         "uz": "Pasport nazorati qayerda?"},
            {"ar": "أَيْنَ الْحَقَائِبُ؟",          "trans": "Айна-ль-хакаиб?",          "ru": "Где багаж?",                         "tj": "Бор куҷост?",                        "en": "Where is the baggage?",              "uz": "Bagaj qayerda?"},
            {"ar": "أُرِيدُ شَرِيحَةَ جَوَّال",    "trans": "Уриду шарихат джавваль",   "ru": "Мне нужна SIM-карта",               "tj": "Ба ман СИМ-карта лозим аст",        "en": "I need a SIM card",                 "uz": "Menga SIM-karta kerak"},
            {"ar": "أَيْنَ الْخُرُوجُ؟",            "trans": "Айна-ль-хурудж?",          "ru": "Где выход?",                         "tj": "Баромад куҷост?",                    "en": "Where is the exit?",                "uz": "Chiqish qayerda?"},
            {"ar": "أَيْنَ التَّاكْسِي؟",           "trans": "Айна-т-такси?",             "ru": "Где такси?",                         "tj": "Такси куҷост?",                      "en": "Where is the taxi?",                "uz": "Taksi qayerda?"},
            {"ar": "أَيْنَ الصَّرَّافَةُ؟",         "trans": "Айна-с-саррафа?",          "ru": "Где обмен валюты?",                 "tj": "Ҷои иваз кардани асъор куҷост?",   "en": "Where is the currency exchange?",   "uz": "Valyuta almashtirish qayerda?"},
            {"ar": "سَاعِدْنِي فِي الْحَقَائِبِ",  "trans": "Саидни фи-ль-хакаиб",      "ru": "Помогите с багажом",                "tj": "Дар бор ба ман кӯмак кунед",       "en": "Help me with the luggage",          "uz": "Bagaj bilan yordam bering"},
        ],
    },

    "taxi": {
        "emoji": "🚕",
        "title_ru": "Такси", "title_tj": "Такси", "title_en": "Taxi", "title_uz": "Taksi",
        "phrases": [
            {"ar": "فَاضِي؟",                       "trans": "Фады?",                    "ru": "Свободен?",                         "tj": "Холӣ ҳастӣ?",                       "en": "Are you free?",                     "uz": "Bo'shsizmi?"},
            {"ar": "إِلَى الْحَرَمِ، بِكَمْ؟",     "trans": "Иля-ль-Харам, бикам?",    "ru": "До Харама, сколько?",               "tj": "То Ҳарам, чанд?",                   "en": "To the Haram, how much?",           "uz": "Haramgacha, qancha?"},
            {"ar": "إِلَى الْمَدِينَةِ، بِكَمْ؟",  "trans": "Иля-ль-Мадина, бикам?",   "ru": "До Медины, сколько?",               "tj": "То Мадина, чанд?",                  "en": "To Madinah, how much?",             "uz": "Madinagacha, qancha?"},
            {"ar": "شَغِّلِ الْعَدَّاد",            "trans": "Шаггиль-аль-аддад",        "ru": "Включи счётчик",                    "tj": "Счётчикро равон кун",               "en": "Turn on the meter",                 "uz": "Hisoblagichni yoq"},
            {"ar": "لَا، هَذَا غَالٍ!",            "trans": "Ля, хаза гали!",           "ru": "Нет, это дорого!",                  "tj": "Не, ин гарон аст!",                 "en": "No, this is expensive!",            "uz": "Yo'q, bu qimmat!"},
            {"ar": "مُمْكِنْ بِعِشْرِينَ رِيَال؟", "trans": "Мумкин би ишрин риял?",   "ru": "Можно за 20 риалов?",              "tj": "Оё 20 риял мешавад?",               "en": "Can we do it for 20 riyals?",       "uz": "20 riyalga bo'ladimi?"},
            {"ar": "قِفْ هُنَا",                    "trans": "Киф хуна",                 "ru": "Остановись здесь",                  "tj": "Инҷо бист",                         "en": "Stop here",                         "uz": "Shu yerda to'xta"},
            {"ar": "يَلَّا!",                       "trans": "Йалла!",                   "ru": "Поехали!",                          "tj": "Биравем!",                          "en": "Let's go!",                         "uz": "Ketdik!"},
            {"ar": "انْتَظِرْنِي",                  "trans": "Интазирни",                "ru": "Подожди меня",                      "tj": "Маро интизор шав",                  "en": "Wait for me",                       "uz": "Meni kut"},
            {"ar": "هَذَا بَعِيدٌ كَثِيرًا",       "trans": "Хаза баид кясир",          "ru": "Это слишком далеко",                "tj": "Ин хеле дур аст",                   "en": "This is too far",                   "uz": "Bu juda uzoq"},
        ],
    },

    "hotel": {
        "emoji": "🏨",
        "title_ru": "Отель", "title_tj": "Меҳмонхона", "title_en": "Hotel", "title_uz": "Mehmonxona",
        "phrases": [
            {"ar": "أَيْنَ فُنْدُقِي؟",             "trans": "Айна фундуки?",            "ru": "Где мой отель?",                    "tj": "Меҳмонхонаи ман куҷост?",           "en": "Where is my hotel?",                "uz": "Mening mehmonxonam qayerda?"},
            {"ar": "هَذَا حَجْزِي",                 "trans": "Хаза хаджзи",             "ru": "Вот моя бронь",                     "tj": "Ин бронии ман аст",                 "en": "This is my reservation",            "uz": "Mana mening bronym"},
            {"ar": "هَذَا جَوَازِي",                "trans": "Хаза джавази",             "ru": "Вот мой паспорт",                   "tj": "Ин паспорти ман аст",               "en": "This is my passport",               "uz": "Mana mening pasportim"},
            {"ar": "ضَيَّعْتُ مِفْتَاحَ الْغُرْفَةِ","trans": "Дайяту мифтах аль-гурфа","ru": "Потерял ключ от комнаты",           "tj": "Калиди хонаро гум кардам",          "en": "I lost my room key",                "uz": "Xona kalitini yo'qotdim"},
            {"ar": "أَيْنَ بَاصٌ إِلَى الْحَرَمِ?", "trans": "Айна бас иля-ль-Харам?", "ru": "Где автобус до Харама?",            "tj": "Автобус ба Ҳарам куҷост?",         "en": "Where is the bus to the Haram?",    "uz": "Haramga avtobus qayerda?"},
            {"ar": "مَتَى الْفُطُورُ؟",             "trans": "Мата-ль-футур?",           "ru": "Когда завтрак?",                    "tj": "Наҳорӣ кай аст?",                   "en": "When is breakfast?",                "uz": "Nonushta qachon?"},
            {"ar": "كَمْ رَقْمُ الْغُرْفَةِ؟",      "trans": "Кям ракму-ль-гурфа?",     "ru": "Какой номер комнаты?",              "tj": "Рақами хона чанд аст?",             "en": "What is the room number?",          "uz": "Xona raqami nechta?"},
            {"ar": "أُرِيدُ غُرْفَةً أُخْرَى",      "trans": "Уриду гурфат ухра",        "ru": "Мне нужен другой номер",            "tj": "Ба ман хонаи дигар лозим аст",      "en": "I need another room",               "uz": "Menga boshqa xona kerak"},
        ],
    },

    "market": {
        "emoji": "🛍",
        "title_ru": "Рынок / Торг", "title_tj": "Бозор / Савдо", "title_en": "Market / Bargaining", "title_uz": "Bozor / Savdo",
        "phrases": [
            {"ar": "بِكَمْ هَذَا؟",                 "trans": "Бикам хаза?",              "ru": "Сколько это стоит?",                "tj": "Ин чанд аст?",                      "en": "How much is this?",                 "uz": "Bu qancha turadi?"},
            {"ar": "لَا، هَذَا غَالٍ!",            "trans": "Ля, хаза гали!",           "ru": "Нет, это дорого!",                  "tj": "Не, ин гарон аст!",                 "en": "No, this is expensive!",            "uz": "Yo'q, bu qimmat!"},
            {"ar": "لَا، رَخِيصٌ كَثِيرًا!",       "trans": "Ля, рахис кясир!",         "ru": "Нет, очень дёшево!",               "tj": "Не, хеле арзон аст!",               "en": "No, very cheap!",                   "uz": "Yo'q, juda arzon!"},
            {"ar": "سَوِّي خَصْمًا",                "trans": "Савви хасм",               "ru": "Сделай скидку",                     "tj": "Тахфиф деҳ",                        "en": "Give me a discount",                "uz": "Chegirma qil"},
            {"ar": "رَخِّصْ شْوَيَّة",              "trans": "Раххис швайя",             "ru": "Уступи немного",                    "tj": "Каме арзон кун",                    "en": "Lower the price a little",          "uz": "Ozroq arzonlashtir"},
            {"ar": "آخِرُ كَلَامٍ كَمْ؟",           "trans": "Ахир калям кям?",          "ru": "Последняя цена?",                   "tj": "Охирин нарх чанд?",                 "en": "What is your last price?",          "uz": "Oxirgi narx qancha?"},
            {"ar": "مُمْكِنْ بِعَشَرَة؟",           "trans": "Мумкин би ашара?",         "ru": "Можно за 10?",                      "tj": "Оё ба даҳ мешавад?",                "en": "Can I get it for 10?",              "uz": "10 ga bo'ladimi?"},
            {"ar": "هَاتِي الْبَاقِي",              "trans": "Хати-ль-баки",             "ru": "Дай сдачу",                         "tj": "Бақиямандро деҳ",                   "en": "Give me the change",                "uz": "Qaytimni ber"},
            {"ar": "لَا، شُكْرًا، أَنَا مَاشِي",   "trans": "Ля, шукран, ана маши",    "ru": "Нет, спасибо, я ухожу",            "tj": "Не, ташаккур, ман меравам",         "en": "No, thank you, I'm leaving",       "uz": "Yo'q, rahmat, men ketayapman"},
            {"ar": "أُرِيدُ مَقَاسًا أَكْبَرَ",     "trans": "Уриду макас акбар",        "ru": "Нужен размер больше",               "tj": "Андозаи калонтар лозим аст",        "en": "I need a bigger size",              "uz": "Kattaroq o'lcham kerak"},
            {"ar": "أُرِيدُ مَقَاسًا أَصْغَرَ",     "trans": "Уриду макас асгар",        "ru": "Нужен размер меньше",               "tj": "Андозаи хурдтар лозим аст",         "en": "I need a smaller size",             "uz": "Kichikroq o'lcham kerak"},
            {"ar": "فِي لَوْنٍ ثَانٍ؟",             "trans": "Фи ляун тани?",            "ru": "Есть другой цвет?",                 "tj": "Рангдонаи дигар ҳаст?",             "en": "Is there another color?",           "uz": "Boshqa rang bormi?"},
            {"ar": "أُرِيدُ غَيْرَهُ",               "trans": "Уриду гайрух",             "ru": "Покажи другой",                     "tj": "Дигарашро нишон деҳ",               "en": "Show me another one",               "uz": "Boshqasini ko'rsat"},
            {"ar": "بَسْ أَشُوفُ",                   "trans": "Бас ашуф",                 "ru": "Я только смотрю",                   "tj": "Танҳо мебинам",                     "en": "I'm just looking",                  "uz": "Men faqat qarayapman"},
        ],
    },

    "cafe": {
        "emoji": "🍽",
        "title_ru": "Кафе / Ресторан", "title_tj": "Кафе / Тарабхона", "title_en": "Cafe / Restaurant", "title_uz": "Kafe / Restoran",
        "phrases": [
            {"ar": "الْمَنْيُو مِنْ فَضْلِكَ",      "trans": "Аль-маньу, мин фадлик",   "ru": "Меню, пожалуйста",                  "tj": "Менюро лутфан биёред",              "en": "The menu, please",                  "uz": "Menyu, iltimos"},
            {"ar": "رُزٌّ مَعَ دَجَاجٍ",             "trans": "Рузз маа даджадж",         "ru": "Рис с курицей",                     "tj": "Биринҷ бо мурғ",                    "en": "Rice with chicken",                 "uz": "Guruch va tovuq"},
            {"ar": "لَحْمٌ",                          "trans": "Лахм",                     "ru": "Мясо",                              "tj": "Гӯшт",                              "en": "Meat",                              "uz": "Go'sht"},
            {"ar": "سَمَكٌ",                          "trans": "Самак",                    "ru": "Рыба",                              "tj": "Моҳӣ",                              "en": "Fish",                              "uz": "Baliq"},
            {"ar": "بِدُونَ حَارٍّ",                  "trans": "Бидун харр",               "ru": "Без острого",                       "tj": "Бе тунд",                           "en": "Without spicy",                     "uz": "Achchiqsiz"},
            {"ar": "بِدُونَ فِلْفِلٍ",               "trans": "Бидун фильфиль",           "ru": "Без перца",                         "tj": "Бе қалампур",                       "en": "Without pepper",                    "uz": "Qalampírsiz"},
            {"ar": "مَاءٌ بَارِدٌ",                   "trans": "Маа барид",                "ru": "Холодная вода",                     "tj": "Оби хунук",                         "en": "Cold water",                        "uz": "Sovuq suv"},
            {"ar": "شَايٌ",                           "trans": "Шай",                      "ru": "Чай",                               "tj": "Чой",                               "en": "Tea",                               "uz": "Choy"},
            {"ar": "قَهْوَةٌ",                        "trans": "Кахва",                    "ru": "Кофе",                              "tj": "Қаҳва",                             "en": "Coffee",                            "uz": "Qahva"},
            {"ar": "الْحِسَابُ مِنْ فَضْلِكَ",       "trans": "Аль-хисаб, мин фадлик",   "ru": "Счёт, пожалуйста",                 "tj": "Ҳисобро лутфан биёред",             "en": "The bill, please",                  "uz": "Hisobni iltimos"},
            {"ar": "سَفَرِي",                         "trans": "Сафари",                   "ru": "С собой (на вынос)",               "tj": "Бо худ (бурданӣ)",                  "en": "To go (takeaway)",                  "uz": "Olib ketish uchun"},
            {"ar": "مَحَلِّي",                        "trans": "Махалли",                  "ru": "Здесь (в кафе)",                   "tj": "Инҷо (дар кафе)",                   "en": "Here (dine in)",                    "uz": "Shu yerda (kafeda)"},
            {"ar": "هَذَا لَذِيذٌ!",                  "trans": "Хаза лязиз!",              "ru": "Это вкусно!",                       "tj": "Ин хеле хуш маза аст!",             "en": "This is delicious!",                "uz": "Bu juda mazali!"},
            {"ar": "وَاحِدٌ ثَانٍ",                   "trans": "Вахид тани",               "ru": "Ещё один / одну",                  "tj": "Боз як дона",                       "en": "One more",                          "uz": "Yana bitta"},
        ],
    },

    "mosque": {
        "emoji": "🕌",
        "title_ru": "Мечеть / Помощь", "title_tj": "Масҷид / Ёрдам", "title_en": "Mosque / Help", "title_uz": "Masjid / Yordam",
        "phrases": [
            {"ar": "أَيْنَ دُخُولُ الرِّجَالِ؟",    "trans": "Айна духуль ар-риджаль?", "ru": "Где вход для мужчин?",              "tj": "Даромади мардон куҷост?",           "en": "Where is the men's entrance?",      "uz": "Erkaklar kirishi qayerda?"},
            {"ar": "أَيْنَ دُخُولُ النِّسَاءِ؟",    "trans": "Айна духуль ан-нисаа?",   "ru": "Где вход для женщин?",              "tj": "Даромади занон куҷост?",            "en": "Where is the women's entrance?",    "uz": "Ayollar kirishi qayerda?"},
            {"ar": "أَيْنَ الْحَمَّامُ؟",            "trans": "Айна-ль-хаммам?",          "ru": "Где туалет?",                       "tj": "Ҳоҷатхона куҷост?",                 "en": "Where is the toilet?",              "uz": "Hojatxona qayerda?"},
            {"ar": "أَيْنَ الْوُضُوءُ؟",             "trans": "Айна-ль-вуду?",            "ru": "Где место для омовения?",           "tj": "Ҷои таҳорат куҷост?",              "en": "Where is the ablution area?",       "uz": "Tahorat joyi qayerda?"},
            {"ar": "أَيْنَ مَاءُ زَمْزَمَ؟",        "trans": "Айна маа Замзам?",         "ru": "Где вода Замзам?",                  "tj": "Оби Замзам куҷост?",                "en": "Where is the Zamzam water?",        "uz": "Zamzam suvi qayerda?"},
            {"ar": "سَاعِدْنِي مِنْ فَضْلِكَ",      "trans": "Саидни, мин фадлик",       "ru": "Помогите мне, пожалуйста",          "tj": "Лутфан ба ман кӯмак кунед",        "en": "Please help me",                    "uz": "Iltimos, menga yordam bering"},
            {"ar": "أَنَا تَائِهٌ",                   "trans": "Ана таих",                 "ru": "Я потерялся",                       "tj": "Ман гум шудам",                     "en": "I am lost",                         "uz": "Men adashib qoldim"},
            {"ar": "أَيْنَ الصَّيْدَلِيَّةُ؟",      "trans": "Айна-с-сайдалия?",         "ru": "Где аптека?",                       "tj": "Дорухона куҷост?",                  "en": "Where is the pharmacy?",            "uz": "Dorixona qayerda?"},
            {"ar": "أَنَا تَعْبَانٌ، أَحْتَاجُ مُسَاعَدَةً", "trans": "Ана тааban, ахтадж мусаада", "ru": "Мне плохо, нужна помощь", "tj": "Ман беҳол ҳастам, кӯмак лозим аст", "en": "I feel unwell, I need help",      "uz": "Menga yomon, yordam kerak"},
            {"ar": "أَيْنَ أَقْرَبُ مُسْتَشْفَى؟",  "trans": "Айна акраб мусташ-фа?",   "ru": "Где ближайшая больница?",           "tj": "Наздиктарин беморхона куҷост?",    "en": "Where is the nearest hospital?",    "uz": "Eng yaqin kasalxona qayerda?"},
            {"ar": "أَيْنَ الْكَعْبَةُ؟",            "trans": "Айна-ль-Кааба?",           "ru": "Где Кааба?",                        "tj": "Каъба куҷост?",                     "en": "Where is the Kaaba?",               "uz": "Kaaba qayerda?"},
            {"ar": "كَمْ شَوْطًا تَبَقَّى؟",         "trans": "Кям шавтан табакка?",      "ru": "Сколько кругов осталось?",          "tj": "Чанд давр мондааст?",               "en": "How many rounds are left?",         "uz": "Nechta aylanish qoldi?"},
        ],
    },
}


import random
import re

SECTION_KEYS = list(SECTIONS.keys())


def get_phrase(sec_idx: int, ph_idx: int) -> dict | None:
    if 0 <= sec_idx < len(SECTION_KEYS):
        phrases = SECTIONS[SECTION_KEYS[sec_idx]]["phrases"]
        if 0 <= ph_idx < len(phrases):
            return phrases[ph_idx]
    return None


def get_test_phrases(section_key: str, count: int = 10) -> list:
    sec_idx = SECTION_KEYS.index(section_key)
    indices = list(range(len(SECTIONS[section_key]["phrases"])))
    if len(indices) > count:
        indices = random.sample(indices, count)
    random.shuffle(indices)
    return [[sec_idx, i] for i in indices]


def make_guide_choices(correct_sec_idx: int, correct_ph_idx: int) -> list:
    all_refs = [
        (i, j)
        for i, key in enumerate(SECTION_KEYS)
        for j in range(len(SECTIONS[key]["phrases"]))
        if (i, j) != (correct_sec_idx, correct_ph_idx)
    ]
    distractors = random.sample(all_refs, 3)
    choices = list(distractors) + [(correct_sec_idx, correct_ph_idx)]
    random.shuffle(choices)
    return choices


def check_guide_answer(user_text: str, phrase: dict, lang: str = "ru") -> bool:
    correct = phrase.get(lang, phrase["ru"]).strip().lower()
    correct_clean = re.sub(r'\s*\([^)]*\)', '', correct).strip()
    answer = user_text.strip().lower()
    return answer == correct or answer == correct_clean or (correct_clean and correct_clean in answer)


LANG_FLAGS = {"ru": "🇷🇺", "tj": "🇹🇯", "en": "🇬🇧", "uz": "🇺🇿"}


def format_section(key: str, lang: str = "ru") -> str:
    """Return formatted text for a guide section in the given language."""
    sec = SECTIONS.get(key)
    if not sec:
        return "Раздел не найден."
    title = sec.get(f"title_{lang}", sec["title_ru"])
    flag = LANG_FLAGS.get(lang, "🇷🇺")
    lines = [f"{sec['emoji']} <b>{title}</b>\n"]
    for p in sec["phrases"]:
        lines.append(f"<blockquote><b>{p['ar']}</b></blockquote>")
        lines.append(f"📢 {p['trans']}")
        lines.append(f"{flag} {p.get(lang, p['ru'])}\n")
    return "\n".join(lines)

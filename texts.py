"""Bot UI strings in 4 languages: ru (русский), tj (тоҷикӣ), en (English), uz (oʻzbek).

Add a new key: copy an existing key, translate to all 4 languages.
Use t(lang, key, **kwargs) — falls back to ru if a key/lang is missing.
"""

TEXTS = {
    # ═══════════════════════════════════════════════════════════════
    #  🇷🇺 РУССКИЙ
    # ═══════════════════════════════════════════════════════════════
    "ru": {
        "choose_lang": "Привет! / Салом! / Hello! / Salom!\n\nВыбери язык обучения:",
        "ask_name": "Как тебя зовут? Напиши своё имя:",
        "welcome": (
            "السلام عليكم ورحمة الله وبركاته\n\n"
            "Добро пожаловать, {name}!\n\n"
            "Да укрепит тебя Аллах на пути знания. Как сказал Всевышний:\n\n"
            "<i>«Скажи: разве равны те, которые знают, и те, которые не знают?»</i>\n"
            "(Сура аз-Зумар, 39:9)\n\n"
            "Маленькими шагами — вперёд. 🌿"
        ),
        "main_menu": "Главное меню:",
        "choose_book": "📚 <b>Выбери уровень обучения</b>\n\nВсе тома открыты — выбирай по своим знаниям:",
        "book_picked": "✅ Ты выбрал: <b>{title}</b>\n👤 Автор: {author}\n\nНачинаем с урока {lesson}.",
        "word_card": "📝 Слово {current} из {total}\n━━━━━━━━━━━━━━━━━\n\n<blockquote><b>{ar}</b></blockquote>\n\n🔊 <i>{trans}</i>\n\n━━━━━━━━━━━━━━━━━\n📖 {translation}",
        "visual_question": "❓ Что означает:\n\n<blockquote><b>{ar}</b></blockquote>\n\n🔊 <i>{trans}</i>",
        "visual_correct": "✅ Правильно!",
        "visual_wrong": "❌ Неверно. Правильный ответ: <b>{correct}</b>",
        "written_question": "✍️ Переведи:\n\n<blockquote><b>{ar}</b></blockquote>\n\n🔊 <i>{trans}</i>",
        "written_correct": "✅ Верно!",
        "written_wrong": "❌ Неверно. Правильно: <b>{correct}</b>",
        "lesson_passed": "🎉 Урок {lesson} пройден!",
        "start_visual": "🎯 Начинаем визуальный тест!",
        "start_written": "✍️ Теперь письменный тест!",
        "visual_done_motivation": "🎉 <b>Молодец!</b> Визуальный тест пройден!\n\n«И скажи: Господи, прибавь мне знания!» (Та-Ха 20:114)\n\nТеперь выбери письменный тест:",
        "choose_written_mode": "✍️ Выбери режим письменного теста:",
        "btn_write_translation": "✍️ Написать перевод",
        "btn_write_arabic": "🕌 Написать арабский",
        "written_arabic_question": "🕌 Напиши на арабском (с огласовками или без):\n\n<blockquote><b>{translation}</b></blockquote>",
        "arabic_correct": "✅ Машаллах, правильно!",
        "arabic_wrong": "❌ Неверно. Правильно: <b>{correct}</b>",
        "failures_visual": "Повторяем урок...",
        "failures_written": "Возвращаемся к визуальному тесту...",
        "weekly_start": "🏆 <b>Еженедельный тест!</b>\n25 слов. Удачи!",
        "weekly_passed": "🎉 Еженедельный тест пройден!",
        "weekly_failed": "Тест не пройден. Повторяем все 70 слов...",
        "rank_up": "📈 Поднялся на {n} позиций в рейтинге!",
        "rank_down": "📉 Опустился на {n} позиций. Не сдавайся!",
        "rank_same": "🏆 Твоё место в рейтинге: #{rank} из {total}",
        "btn_next": "➡️ Следующее",
        "btn_learned": "✅ Выучил",
        "btn_repeat": "🔄 Повторить",
        "btn_lesson": "▶️ Урок",
        "btn_profile": "👤 Профиль",
        "btn_stats": "📊 Статистика",
        "btn_books": "📖 Сменить том",
        "btn_settings": "⚙️ Настройки",
        "btn_ask": "❓ Вопрос учителю",
        "btn_guide": "🕋 Умра Гайд",
        "btn_miniapp": "🌐 Открыть Mini App",
        "btn_guide_test": "🧪 Пройти тест",
        "guide_choose": "🕋 Умра Гайд — выбери раздел:",
        "guide_visual_start": "🎯 Визуальный тест — выбери правильный перевод:",
        "guide_what_means": "❓ Что означает:",
        "guide_visual_done": "✅ Визуальный тест пройден!\n\n✍️ Теперь письменный тест — напиши перевод:",
        "guide_translate": "✍️ Переведи:",
        "guide_correct": "✅ Правильно!",
        "guide_wrong": "❌ Неверно. Правильный ответ: <b>{correct}</b>",
        "guide_restart_test": "🔄 Начинаем тест заново!",
        "guide_restart_visual": "🔄 Возвращаемся к визуальному тесту!",
        "guide_done": "🎉 Машаллах! Тест Умра Гайда пройден! 🕋",
        "ask_reminder": "Введи время напоминания (формат 08:00):",
        "reminder_set": "⏰ Напоминание установлено на {time}",
        "choose_timezone": "🌍 Выбери свой часовой пояс:",
        "timezone_set": "✅ Часовой пояс сохранён! Напоминания будут приходить вовремя. 🕐",
        "ask_question": "✍️ Напиши свой вопрос учителю:",
        "question_sent": "✅ Вопрос отправлен учителю! Ожидай ответа.",
        "question_answered": "📬 Ответ от учителя:\n\n{answer}",
        "no_questions": "Вопросов пока нет.",
        "teacher_menu": "👨‍🏫 Кабинет учителя:",
        "ask_broadcast": "Введи текст рассылки:",
        "broadcast_sent": "✅ Рассылка отправлена {count} ученикам.",
        "ask_personal_msg": "✍️ Напиши сообщение для <b>{name}</b>:",
        "personal_msg_sent": "✅ Сообщение отправлено ученику <b>{name}</b>.",
        "students_empty": "Учеников пока нет.",
        "students_header": "👥 <b>Ученики ({count})</b>\nСортировка по выученным словам:\n\n",
        "lazy_students": "😴 <b>Лентяи (0 слов):</b>\n{list}",
        "no_lazy": "✨ Лентяев нет — все учатся!",
        "stats_text": (
            "📊 <b>Статистика</b>\n\n"
            "📖 {book_title}\n"
            "📚 Урок {lesson} из {total_lessons}\n"
            "✅ Всего выучено: {total_learned} слов\n"
            "📊 В этом томе: {book_learned}/{book_total}\n"
            "{rank_text}"
        ),
        "fail_texts": [
            "🌙 «Не покинул тебя твой Господь» (Ад-Духа 93:3)\n\nПродолжай, ты не один.",
            "💫 «Воистину, с трудом приходит облегчение» (Аш-Шарх 94:6)\n\nЕщё раз — и получится!",
            "🤲 «Кто выйдет на поиск знания — тому Аллах облегчит путь в Рай» (Муслим) Не сдавайся!",
            "🌿 «Аллах не возлагает на душу сверх её возможностей» (Аль-Бакара 2:286) Ты сможешь!",
            "⭐ «Не теряйте надежды на милость Аллаха» (Аз-Зумар 39:53) Держись своей цели!",
            "🏔 «Воистину, Аллах с терпеливыми» (Аль-Бакара 2:153) Терпи, ты на верном пути! Всё получится.",
            "💎 «Терпите, ведь Аллах не теряет награды» (Худ 11:115) Каждое твоё старание записывается как награда.",
            "🌊 «Обрадуй терпеливых» (Аль-Бакара 2:155-156) Не ленись! Ты сможешь!",
        ],
        "reminder_texts": [
            "🌙 «Самые любимые дела перед Аллахом — постоянные, даже если малы» (Бухари)",
            "📖 «Кому Аллах желает блага — того делает сведущим в религии» (Бухари)",
            "🌙 «Скажи: Господи! Прибавь мне знания» (Та-ха 20:114)",
            "💫 «Только те боятся Аллаха, которые обладают знанием» (Фатир 35:28)",
            "🏅 «Аллах возвысит тех, кому даровано знание» (Аль-Муджадала 58:11)",
            "📚 «Читай! Во имя твоего Господа» (Аль-Алак 96:1)",
            "🌿 «Разве равны те, которые знают, и те, которые не знают?» (Аз-Зумар 39:9)",
        ],
    },

    # ═══════════════════════════════════════════════════════════════
    #  🇹🇯 ТОҶИКӢ
    # ═══════════════════════════════════════════════════════════════
    "tj": {
        "choose_lang": "Привет! / Салом! / Hello! / Salom!\n\nЗабонро интихоб кун:",
        "ask_name": "Номатро нависед:",
        "welcome": (
            "السلام عليكم ورحمة الله وبركاته\n\n"
            "Хуш омадед, {name}!\n\n"
            "Аллоҳ туро дар роҳи илм устувор гардонад. Чунон ки Парвардигор фармуд:\n\n"
            "<i>«Бигӯ: оё баробаранд онон ки медонанд ва онон ки намедонанд?»</i>\n"
            "(Сураи Зумар, 39:9)\n\n"
            "Қадам ба қадам — ба пеш. 🌿"
        ),
        "main_menu": "Меню:",
        "choose_book": "📚 <b>Сатҳи омӯзишро интихоб кун</b>\n\nҲамаи ҷилдҳо кушоданд — мувофиқи дониши худ интихоб кун:",
        "book_picked": "✅ Ту интихоб кардӣ: <b>{title}</b>\n👤 Муаллиф: {author}\n\nАз дарси {lesson} оғоз мекунем.",
        "word_card": "📝 Калима {current} аз {total}\n━━━━━━━━━━━━━━━━━\n\n<blockquote><b>{ar}</b></blockquote>\n\n🔊 <i>{trans}</i>\n\n━━━━━━━━━━━━━━━━━\n📖 {translation}",
        "visual_question": "❓ Маънои:\n\n<blockquote><b>{ar}</b></blockquote>\n\n🔊 <i>{trans}</i>",
        "visual_correct": "✅ Дуруст!",
        "visual_wrong": "❌ Нодуруст. Ҷавоби дуруст: <b>{correct}</b>",
        "written_question": "✍️ Тарҷума кун:\n\n<blockquote><b>{ar}</b></blockquote>\n\n🔊 <i>{trans}</i>",
        "written_correct": "✅ Дуруст!",
        "written_wrong": "❌ Нодуруст. Дуруст: <b>{correct}</b>",
        "lesson_passed": "🎉 Дарси {lesson} гузашт!",
        "start_visual": "🎯 Санҷиши визуалӣ!",
        "start_written": "✍️ Санҷиши хаттӣ!",
        "visual_done_motivation": "🎉 <b>Офарин!</b> Санҷиши визуалӣ гузашт!\n\n«Бигӯ: Парвардигоро, илмамро зиёд кун!» (Тоҳо 20:114)\n\nАкнун санҷиши хаттиро интихоб кун:",
        "choose_written_mode": "✍️ Режими санҷиши хаттиро интихоб кун:",
        "btn_write_translation": "✍️ Тарҷума навиштан",
        "btn_write_arabic": "🕌 Арабӣ навиштан",
        "written_arabic_question": "🕌 Ба арабӣ нависед (бо ҳаракот ё бе):\n\n<blockquote><b>{translation}</b></blockquote>",
        "arabic_correct": "✅ Машоаллоҳ, дуруст!",
        "arabic_wrong": "❌ Нодуруст. Дуруст: <b>{correct}</b>",
        "failures_visual": "Дарсро такрор мекунем...",
        "failures_written": "Ба санҷиши визуалӣ бармегардем...",
        "weekly_start": "🏆 <b>Санҷиши ҳафтагӣ!</b>\n25 калима. Муваффақ бош!",
        "weekly_passed": "🎉 Санҷиши ҳафтагӣ гузашт!",
        "weekly_failed": "Санҷиш нагузашт. Ҳамаи 70 калимаро такрор мекунем...",
        "rank_up": "📈 Дар рейтинг {n} зина боло рафтӣ!",
        "rank_down": "📉 {n} зина поён рафтӣ. Аз пай нашав!",
        "rank_same": "🏆 Ҷои ту дар рейтинг: #{rank} аз {total}",
        "btn_next": "➡️ Навбатӣ",
        "btn_learned": "✅ Ёд гирифтам",
        "btn_repeat": "🔄 Такрор",
        "btn_lesson": "▶️ Дарс",
        "btn_profile": "👤 Профил",
        "btn_stats": "📊 Омор",
        "btn_books": "📖 Ҷилдро дигар кун",
        "btn_settings": "⚙️ Танзимот",
        "btn_ask": "❓ Савол ба устод",
        "btn_guide": "🕋 Роҳнамои Умра",
        "btn_miniapp": "🌐 Кушодани Mini App",
        "btn_guide_test": "🧪 Санҷишро гузаштан",
        "guide_choose": "🕋 Роҳнамои Умра — бахшро интихоб кун:",
        "guide_visual_start": "🎯 Санҷиши визуалӣ — тарҷумаи дурустро интихоб кун:",
        "guide_what_means": "❓ Маънои ин чист:",
        "guide_visual_done": "✅ Санҷиши визуалӣ гузашт!\n\n✍️ Акнун санҷиши хаттӣ — тарҷумаро нависед:",
        "guide_translate": "✍️ Тарҷума кун:",
        "guide_correct": "✅ Дуруст!",
        "guide_wrong": "❌ Нодуруст. Ҷавоби дуруст: <b>{correct}</b>",
        "guide_restart_test": "🔄 Санҷишро аз нав оғоз мекунем!",
        "guide_restart_visual": "🔄 Ба санҷиши визуалӣ бармегардем!",
        "guide_done": "🎉 Машоаллоҳ! Санҷиши Роҳнамои Умра гузашт! 🕋",
        "ask_reminder": "Вақти ёдоваркуниро нависед (08:00):",
        "reminder_set": "⏰ Ёдоварӣ дар соати {time} гузошта шуд",
        "choose_timezone": "🌍 Минтақаи вақтии худро интихоб кун:",
        "timezone_set": "✅ Минтақаи вақт сабт шуд! Ёдоварӣ дар вақташ меояд. 🕐",
        "ask_question": "✍️ Саволатро бинавис:",
        "question_sent": "✅ Савол фиристода шуд!",
        "question_answered": "📬 Ҷавоби устод:\n\n{answer}",
        "no_questions": "Саволе нест.",
        "teacher_menu": "👨‍🏫 Кабинети устод:",
        "ask_broadcast": "Матни паёмро нависед:",
        "broadcast_sent": "✅ Паём ба {count} нафар фиристода шуд.",
        "ask_personal_msg": "✍️ Паёмро барои <b>{name}</b> бинавис:",
        "personal_msg_sent": "✅ Паём ба шогирд <b>{name}</b> фиристода шуд.",
        "students_empty": "Шогирде нест.",
        "students_header": "👥 <b>Шогирдон ({count})</b>\nТартиб бо ёд гирифтаҳо:\n\n",
        "lazy_students": "😴 <b>Танбалон (0 калима):</b>\n{list}",
        "no_lazy": "✨ Танбал нест — ҳама меомӯзанд!",
        "stats_text": (
            "📊 <b>Омор</b>\n\n"
            "📖 {book_title}\n"
            "📚 Дарси {lesson} аз {total_lessons}\n"
            "✅ Ҳамагӣ ёд гирифта: {total_learned} калима\n"
            "📊 Дар ин ҷилд: {book_learned}/{book_total}\n"
            "{rank_text}"
        ),
        "fail_texts": [
            "🌙 «Парвардигорат туро тарк накардааст» (Аз-Зуҳо 93:3)\n\nДавом деҳ, ту танҳо нестӣ.",
            "💫 «Бо душворӣ осонӣ меояд» (Аш-Шарҳ 94:6)\n\nБоз як бори дигар — ту метавонӣ!",
            "🤲 «Ҳар ки дар роҳи илм барояд, Аллоҳ роҳи биҳиштро барояш осон мекунад» (Муслим) Таслим нашав!",
            "🌿 «Аллоҳ ба ҳеч кас зиёда аз тавонаш бор намегузорад» (Бақара 2:286) Ту метавонӣ!",
            "⭐ «Аз раҳмати Аллоҳ ноумед нашавед» (Зумар 39:53) Аз ҳадафат даст накаш!",
            "🏔 «Аллоҳ бо сабуркорон аст» (Бақара 2:153) Сабр кун, ту дар роҳи дурустӣ! Ҳама чиз мешавад.",
            "💎 «Сабр кунед, Аллоҳ музди касеро гум намекунад» (Ҳуд 11:115) Ҳар кӯшиши ту ҳамчун савоб навишта мешавад.",
            "🌊 «Сабуркоронро хушхабар деҳ» (Бақара 2:155-156) Танбалӣ накун! Ту метавонӣ!",
        ],
        "reminder_texts": [
            "🌙 «Маҳбубтарин амалҳо назди Аллоҳ доимист» (Бухорӣ)",
            "📖 «Ба ҳар ки Аллоҳ хайр хоҳад, уро дар дин огоҳ мекунад» (Бухорӣ)",
            "🌙 «Бигӯ: Парвардигоро, илмамро зиёд кун» (Тоҳо 20:114)",
            "💫 «Танҳо онон аз Аллоҳ метарсанд ки донишманданд» (Фотир 35:28)",
            "🏅 «Аллоҳ онеро ки илм дода шудааст баланд мекунад» (Муҷодала 58:11)",
            "📚 «Бихон! Ба номи Парвардигорат» (Алақ 96:1)",
            "🌿 «Оё баробаранд онон ки медонанд ва онон ки намедонанд?» (Зумар 39:9)",
        ],
    },

    # ═══════════════════════════════════════════════════════════════
    #  🇬🇧 ENGLISH
    # ═══════════════════════════════════════════════════════════════
    "en": {
        "choose_lang": "Привет! / Салом! / Hello! / Salom!\n\nChoose your learning language:",
        "ask_name": "What's your name? Please type it:",
        "welcome": (
            "السلام عليكم ورحمة الله وبركاته\n\n"
            "Welcome, {name}!\n\n"
            "May Allah strengthen you on the path of knowledge. The Most High said:\n\n"
            "<i>«Say: are those who know equal to those who do not know?»</i>\n"
            "(Surah Az-Zumar, 39:9)\n\n"
            "Step by step — keep going. 🌿"
        ),
        "main_menu": "Main menu:",
        "choose_book": "📚 <b>Choose your level</b>\n\nAll volumes are open — pick by your skill:",
        "book_picked": "✅ You picked: <b>{title}</b>\n👤 Author: {author}\n\nStarting from lesson {lesson}.",
        "word_card": "📝 Word {current} of {total}\n━━━━━━━━━━━━━━━━━\n\n<blockquote><b>{ar}</b></blockquote>\n\n🔊 <i>{trans}</i>\n\n━━━━━━━━━━━━━━━━━\n📖 {translation}",
        "visual_question": "❓ What does this mean?\n\n<blockquote><b>{ar}</b></blockquote>\n\n🔊 <i>{trans}</i>",
        "visual_correct": "✅ Correct!",
        "visual_wrong": "❌ Wrong. Correct answer: <b>{correct}</b>",
        "written_question": "✍️ Translate:\n\n<blockquote><b>{ar}</b></blockquote>\n\n🔊 <i>{trans}</i>",
        "written_correct": "✅ Right!",
        "written_wrong": "❌ Wrong. Correct: <b>{correct}</b>",
        "lesson_passed": "🎉 Lesson {lesson} completed!",
        "start_visual": "🎯 Starting visual test!",
        "start_written": "✍️ Now the written test!",
        "visual_done_motivation": "🎉 <b>Excellent!</b> Visual test passed!\n\n«Say: My Lord, increase me in knowledge!» (Ta-Ha 20:114)\n\nNow pick a written test mode:",
        "choose_written_mode": "✍️ Pick the written test mode:",
        "btn_write_translation": "✍️ Write translation",
        "btn_write_arabic": "🕌 Write in Arabic",
        "written_arabic_question": "🕌 Write in Arabic (with or without diacritics):\n\n<blockquote><b>{translation}</b></blockquote>",
        "arabic_correct": "✅ Mashallah, correct!",
        "arabic_wrong": "❌ Wrong. Correct: <b>{correct}</b>",
        "failures_visual": "Repeating the lesson...",
        "failures_written": "Back to the visual test...",
        "weekly_start": "🏆 <b>Weekly test!</b>\n25 words. Good luck!",
        "weekly_passed": "🎉 Weekly test passed!",
        "weekly_failed": "Test failed. Repeating all 70 words...",
        "rank_up": "📈 You went up {n} positions!",
        "rank_down": "📉 You dropped {n} positions. Don't give up!",
        "rank_same": "🏆 Your rank: #{rank} of {total}",
        "btn_next": "➡️ Next",
        "btn_learned": "✅ Learned",
        "btn_repeat": "🔄 Repeat",
        "btn_lesson": "▶️ Lesson",
        "btn_profile": "👤 Profile",
        "btn_stats": "📊 Stats",
        "btn_books": "📖 Change volume",
        "btn_settings": "⚙️ Settings",
        "btn_ask": "❓ Ask teacher",
        "btn_guide": "🕋 Umrah Guide",
        "btn_miniapp": "🌐 Open Mini App",
        "btn_guide_test": "🧪 Take the test",
        "guide_choose": "🕋 Umrah Guide — choose a section:",
        "guide_visual_start": "🎯 Visual test — choose the correct translation:",
        "guide_what_means": "❓ What does this mean:",
        "guide_visual_done": "✅ Visual test passed!\n\n✍️ Now the written test — write the translation:",
        "guide_translate": "✍️ Translate:",
        "guide_correct": "✅ Correct!",
        "guide_wrong": "❌ Wrong. Correct answer: <b>{correct}</b>",
        "guide_restart_test": "🔄 Starting the test over!",
        "guide_restart_visual": "🔄 Back to the visual test!",
        "guide_done": "🎉 Mashallah! Umrah Guide test passed! 🕋",
        "ask_reminder": "Reminder time (format 08:00):",
        "reminder_set": "⏰ Reminder set at {time}",
        "choose_timezone": "🌍 Pick your timezone:",
        "timezone_set": "✅ Timezone saved! Reminders will arrive on time. 🕐",
        "ask_question": "✍️ Type your question to the teacher:",
        "question_sent": "✅ Question sent! Wait for a reply.",
        "question_answered": "📬 Teacher's answer:\n\n{answer}",
        "no_questions": "No questions yet.",
        "teacher_menu": "👨‍🏫 Teacher dashboard:",
        "ask_broadcast": "Type the broadcast message:",
        "broadcast_sent": "✅ Broadcast sent to {count} students.",
        "ask_personal_msg": "✍️ Write a message for <b>{name}</b>:",
        "personal_msg_sent": "✅ Message sent to <b>{name}</b>.",
        "students_empty": "No students yet.",
        "students_header": "👥 <b>Students ({count})</b>\nSorted by words learned:\n\n",
        "lazy_students": "😴 <b>Slackers (0 words):</b>\n{list}",
        "no_lazy": "✨ No slackers — everyone is learning!",
        "stats_text": (
            "📊 <b>Stats</b>\n\n"
            "📖 {book_title}\n"
            "📚 Lesson {lesson} of {total_lessons}\n"
            "✅ Total learned: {total_learned} words\n"
            "📊 In this volume: {book_learned}/{book_total}\n"
            "{rank_text}"
        ),
        "fail_texts": [
            "🌙 «Your Lord has not forsaken you» (Ad-Duha 93:3)\n\nKeep going, you're not alone.",
            "💫 «Indeed, with hardship comes ease» (Ash-Sharh 94:6)\n\nOne more try!",
            "🤲 «Whoever takes a path seeking knowledge, Allah will ease his way to Paradise» (Muslim)",
            "🌿 «Allah does not burden a soul beyond what it can bear» (Al-Baqarah 2:286)",
            "⭐ «Do not despair of Allah's mercy» (Az-Zumar 39:53)",
            "🏔 «Indeed, Allah is with the patient» (Al-Baqarah 2:153)",
            "💎 «Be patient — Allah does not waste the reward» (Hud 11:115)",
            "🌊 «Give glad tidings to the patient» (Al-Baqarah 2:155-156)",
        ],
        "reminder_texts": [
            "🌙 «The deeds most beloved to Allah are the consistent ones, though small» (Bukhari)",
            "📖 «To whomever Allah wishes good, He grants understanding of religion» (Bukhari)",
            "🌙 «Say: My Lord, increase me in knowledge» (Ta-Ha 20:114)",
            "💫 «Only those of His servants fear Allah who have knowledge» (Fatir 35:28)",
            "🏅 «Allah raises those of you who believe and those given knowledge» (Al-Mujadila 58:11)",
            "📚 «Read! In the name of your Lord» (Al-Alaq 96:1)",
            "🌿 «Are those who know equal to those who do not know?» (Az-Zumar 39:9)",
        ],
    },

    # ═══════════════════════════════════════════════════════════════
    #  🇺🇿 OʻZBEK (Latin)
    # ═══════════════════════════════════════════════════════════════
    "uz": {
        "choose_lang": "Привет! / Салом! / Hello! / Salom!\n\nOʻqish tilini tanlang:",
        "ask_name": "Ismingiz nima? Yozing:",
        "welcome": (
            "السلام عليكم ورحمة الله وبركاته\n\n"
            "Xush kelibsiz, {name}!\n\n"
            "Alloh sizni ilm yoʻlida mustahkam qilsin. Yuksak Alloh aytdi:\n\n"
            "<i>«Ayt: biluvchilar bilan bilmaganlar teng boʻladimi?»</i>\n"
            "(Az-Zumar surasi, 39:9)\n\n"
            "Qadam-baqadam — oldinga. 🌿"
        ),
        "main_menu": "Asosiy menyu:",
        "choose_book": "📚 <b>Daraja tanlang</b>\n\nBarcha jildlar ochiq — bilimingizga qarab tanlang:",
        "book_picked": "✅ Siz tanladingiz: <b>{title}</b>\n👤 Muallif: {author}\n\n{lesson}-darsdan boshlaymiz.",
        "word_card": "📝 Soʻz {current} / {total}\n━━━━━━━━━━━━━━━━━\n\n<blockquote><b>{ar}</b></blockquote>\n\n🔊 <i>{trans}</i>\n\n━━━━━━━━━━━━━━━━━\n📖 {translation}",
        "visual_question": "❓ Bu soʻzning maʼnosi?\n\n<blockquote><b>{ar}</b></blockquote>\n\n🔊 <i>{trans}</i>",
        "visual_correct": "✅ Toʻgʻri!",
        "visual_wrong": "❌ Notoʻgʻri. Toʻgʻri javob: <b>{correct}</b>",
        "written_question": "✍️ Tarjima qiling:\n\n<blockquote><b>{ar}</b></blockquote>\n\n🔊 <i>{trans}</i>",
        "written_correct": "✅ Toʻgʻri!",
        "written_wrong": "❌ Notoʻgʻri. Toʻgʻri: <b>{correct}</b>",
        "lesson_passed": "🎉 {lesson}-dars tugadi!",
        "start_visual": "🎯 Vizual test boshlanadi!",
        "start_written": "✍️ Endi yozma test!",
        "visual_done_motivation": "🎉 <b>Yashang!</b> Vizual test tugadi!\n\n«Ayt: Rabbim, ilmimni ziyoda qil!» (Toha 20:114)\n\nEndi yozma test rejimini tanlang:",
        "choose_written_mode": "✍️ Yozma test rejimini tanlang:",
        "btn_write_translation": "✍️ Tarjima yozish",
        "btn_write_arabic": "🕌 Arabcha yozish",
        "written_arabic_question": "🕌 Arabcha yozing (harakatlar bilan yoki ularsiz):\n\n<blockquote><b>{translation}</b></blockquote>",
        "arabic_correct": "✅ Moshaalloh, toʻgʻri!",
        "arabic_wrong": "❌ Notoʻgʻri. Toʻgʻri: <b>{correct}</b>",
        "failures_visual": "Darsni takrorlaymiz...",
        "failures_written": "Vizual testga qaytamiz...",
        "weekly_start": "🏆 <b>Haftalik test!</b>\n25 ta soʻz. Omad!",
        "weekly_passed": "🎉 Haftalik test tugadi!",
        "weekly_failed": "Test oʻtmadi. Barcha 70 ta soʻzni takrorlaymiz...",
        "rank_up": "📈 Reytingda {n} pogʻona koʻtarildingiz!",
        "rank_down": "📉 {n} pogʻona pasaydingiz. Taslim boʻlmang!",
        "rank_same": "🏆 Reyting oʻrningiz: #{rank} / {total}",
        "btn_next": "➡️ Keyingi",
        "btn_learned": "✅ Oʻrgandim",
        "btn_repeat": "🔄 Qaytarish",
        "btn_lesson": "▶️ Dars",
        "btn_profile": "👤 Profil",
        "btn_stats": "📊 Statistika",
        "btn_books": "📖 Jildni almashtirish",
        "btn_settings": "⚙️ Sozlamalar",
        "btn_ask": "❓ Ustozga savol",
        "btn_guide": "🕋 Umra Gid",
        "btn_miniapp": "🌐 Mini Appni ochish",
        "btn_guide_test": "🧪 Testni boshlash",
        "guide_choose": "🕋 Umra Gid — bo'limni tanlang:",
        "guide_visual_start": "🎯 Vizual test — to'g'ri tarjimani tanlang:",
        "guide_what_means": "❓ Bu nima degani:",
        "guide_visual_done": "✅ Vizual test o'tdi!\n\n✍️ Endi yozma test — tarjimani yozing:",
        "guide_translate": "✍️ Tarjima qiling:",
        "guide_correct": "✅ To'g'ri!",
        "guide_wrong": "❌ Noto'g'ri. To'g'ri javob: <b>{correct}</b>",
        "guide_restart_test": "🔄 Testni qaytadan boshlaymiz!",
        "guide_restart_visual": "🔄 Vizual testga qaytamiz!",
        "guide_done": "🎉 Mashaalloh! Umra Gid testi o'tdi! 🕋",
        "ask_reminder": "Eslatma vaqtini kiriting (08:00):",
        "reminder_set": "⏰ Eslatma {time} ga oʻrnatildi",
        "choose_timezone": "🌍 Vaqt mintaqasini tanlang:",
        "timezone_set": "✅ Vaqt mintaqasi saqlandi! Eslatma oʻz vaqtida keladi. 🕐",
        "ask_question": "✍️ Ustozga savolingizni yozing:",
        "question_sent": "✅ Savol yuborildi! Javobni kuting.",
        "question_answered": "📬 Ustoz javobi:\n\n{answer}",
        "no_questions": "Hozircha savollar yoʻq.",
        "teacher_menu": "👨‍🏫 Ustoz kabineti:",
        "ask_broadcast": "Yuboriladigan matnni yozing:",
        "broadcast_sent": "✅ Xabar {count} ta oʻquvchiga yuborildi.",
        "ask_personal_msg": "✍️ <b>{name}</b> uchun xabar yozing:",
        "personal_msg_sent": "✅ Xabar <b>{name}</b> ga yuborildi.",
        "students_empty": "Hozircha oʻquvchilar yoʻq.",
        "students_header": "👥 <b>Oʻquvchilar ({count})</b>\nOʻrgangan soʻzlar boʻyicha:\n\n",
        "lazy_students": "😴 <b>Dangasalar (0 soʻz):</b>\n{list}",
        "no_lazy": "✨ Dangasalar yoʻq — barcha oʻrganmoqda!",
        "stats_text": (
            "📊 <b>Statistika</b>\n\n"
            "📖 {book_title}\n"
            "📚 Dars {lesson} / {total_lessons}\n"
            "✅ Jami oʻrganildi: {total_learned} ta soʻz\n"
            "📊 Bu jildda: {book_learned}/{book_total}\n"
            "{rank_text}"
        ),
        "fail_texts": [
            "🌙 «Rabbing seni tark etmadi» (Ad-Duho 93:3)\n\nDavom et, yolgʻiz emassan.",
            "💫 «Albatta, qiyinchilik bilan birga osonlik bor» (Ash-Sharh 94:6)\n\nYana bir bor — boʻladi!",
            "🤲 «Kim ilm yoʻlida yursa, Alloh unga jannat yoʻlini osonlashtiradi» (Muslim)",
            "🌿 «Alloh hech kimga kuchi yetmaydigan narsani yuklamaydi» (Al-Baqara 2:286)",
            "⭐ «Allohning rahmatidan umid uzmang» (Az-Zumar 39:53)",
            "🏔 «Albatta, Alloh sabrlilar bilandir» (Al-Baqara 2:153)",
            "💎 «Sabr qiling — Alloh ajrni zoye qilmaydi» (Hud 11:115)",
            "🌊 «Sabrlilarga xushxabar ber» (Al-Baqara 2:155-156)",
        ],
        "reminder_texts": [
            "🌙 «Alloh huzurida sevimli amallar — kam boʻlsa-da, doimiy boʻlganlardir» (Buxoriy)",
            "📖 «Alloh kimga yaxshilik istasa, uni dinda fiqhli qiladi» (Buxoriy)",
            "🌙 «Ayt: Rabbim, ilmimni ziyoda qil» (Toha 20:114)",
            "💫 «Allohdan faqat olimlar qoʻrqadilar» (Fotir 35:28)",
            "🏅 «Alloh ilm berilganlarning darajalarini koʻtaradi» (Al-Mujodila 58:11)",
            "📚 «Oʻqi! Rabbing nomi bilan» (Al-Alaq 96:1)",
            "🌿 «Biluvchilar bilan bilmaganlar teng boʻladimi?» (Az-Zumar 39:9)",
        ],
    },
}


SUPPORTED_LANGS = ("ru", "tj", "en", "uz")


def t(lang: str, key: str, **kwargs) -> str:
    """Translate with fallback chain: lang -> ru -> key."""
    if lang not in TEXTS:
        lang = "ru"
    text = TEXTS[lang].get(key) or TEXTS["ru"].get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text
    return text


def get_fail_text(lang: str, index: int) -> str:
    texts = TEXTS.get(lang, TEXTS["ru"]).get("fail_texts") or TEXTS["ru"]["fail_texts"]
    return texts[index % len(texts)]


def get_reminder_text(lang: str, weekday: int) -> str:
    texts = TEXTS.get(lang, TEXTS["ru"]).get("reminder_texts") or TEXTS["ru"]["reminder_texts"]
    return texts[weekday % len(texts)]

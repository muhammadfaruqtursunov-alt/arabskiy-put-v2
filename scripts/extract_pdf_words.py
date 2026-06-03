"""Extract ALL word triplets from Medina course PDFs into JSON.

Strategy:
1. Use pymupdf (fitz) — better Arabic extraction than pypdf
2. NFKC normalize → presentation forms become standard Arabic
3. Strip control chars (PDF rendering artifacts that replaced shadda/etc)
4. Parse triplet pattern: Arabic+Tajik (one line) → Russian (next line)
   OR: Arabic (line) → Tajik (line) → Russian (line)

Usage:
    python scripts/extract_pdf_words.py
"""
import json
import re
import sys
import io
import unicodedata
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import fitz  # pymupdf


# Unicode ranges
ARABIC_RE = re.compile(r'[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]')
CYRILLIC_RE = re.compile(r'[Ѐ-ӿ]')
# Diacritic marks we want to preserve
DIACRITICS = 'ًٌٍَُِّْـ'


def strip_controls(s: str) -> str:
    """Remove ASCII/Latin-1 control chars (PDF rendering artifacts) but keep newlines."""
    return ''.join(c for c in s if c.isprintable() or c == '\n')


def is_arabic(s: str) -> bool:
    return bool(ARABIC_RE.search(s))


def is_cyrillic(s: str) -> bool:
    return bool(CYRILLIC_RE.search(s))


def starts_arabic(s: str) -> bool:
    if not s:
        return False
    return bool(ARABIC_RE.match(s[0]))


def split_arabic_cyrillic(line: str):
    """If a line is 'ArabicWord<no-space>CyrillicTranslation', split them."""
    m = re.match(r'^([؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿\s' + DIACRITICS + r']+?)([Ѐ-ӿ].*)$', line)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return line.strip(), ''


def clean_text(s: str) -> str:
    """Replace tabs and collapse whitespace."""
    s = s.replace('\t', ' ')
    return ' '.join(s.split())


def clean_arabic(s: str) -> str:
    """Final pass on Arabic — strip non-Arabic non-diacritic chars, remove internal spaces."""
    s = strip_controls(s)
    # Drop anything that isn't Arabic letter or diacritic
    result = ''.join(c for c in s
                     if ARABIC_RE.match(c) or c in DIACRITICS or c == ' ')
    result = re.sub(r'\s+', '', result)
    # Common PDF artifact: definite article alef-lam loses the lam.
    # "اْX" → "الْX" (when followed by another Arabic letter)
    result = re.sub(r'^اْ(?=[ا-ي])', 'الْ', result)
    return result


def clean_translation(s: str) -> str:
    """Clean tajik/russian: remove embedded Arabic, normalize whitespace."""
    s = strip_controls(s)
    s = s.replace('\t', ' ')
    # Remove parenthesized notes that contain Arabic (PDF side-notes)
    s = re.sub(r'\([^)]*[؀-ۿ][^)]*\)', '', s)
    s = re.sub(r'[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]', '', s)  # strip any remaining Arabic
    return ' '.join(s.split())


# Manual fixes for words that lose letters in PDF extraction.
# Map: bad_arabic -> proper_arabic
ARABIC_FIXES = {
    'َكِن': 'لَكِنَّ',
    'َعَ': 'لَعَلَّ',
    'َيْتَ': 'لَيْتَ',
    'كََن': 'كَأَنَّ',
    'جِحٌ': 'نَاجِحٌ',
    'مُتزَوِّجٌ': 'مُتَزَوِّجٌ',
    'مُتزَوِّجَةٌ': 'مُتَزَوِّجَةٌ',
    'أَكْبرَُ': 'أَكْبَرُ',
    'أَطْوَلُ': 'أَطْوَلُ',
    'أَجْمَُ': 'أَجْمَلُ',
    'أَسْهَُ': 'أَسْهَلُ',
    'أَنْظَفُ': 'أَنْظَفُ',
    'إِن': 'إِنَّ',
    'إِنهُ': 'إِنَّهُ',
    'إِنهَ': 'إِنَّهَا',
    'إِنكَ': 'إِنَّكَ',
    'إِنكِ': 'إِنَّكِ',
    'إِنكُمْ': 'إِنَّكُمْ',
    'إِننَ': 'إِنَّنَا',
    'إِنهُمْ': 'إِنَّهُمْ',
}


def extract_pdf(path: Path) -> list:
    doc = fitz.open(str(path))
    text = '\n'.join(p.get_text() for p in doc)
    text = unicodedata.normalize('NFKC', text)
    text = strip_controls(text)

    raw_lines = [l.strip() for l in text.split('\n') if l.strip()]

    # Pre-process: split mixed Arabic+Cyrillic lines into two
    lines = []
    for line in raw_lines:
        if is_arabic(line) and is_cyrillic(line) and starts_arabic(line):
            ar, cy = split_arabic_cyrillic(line)
            if ar and cy:
                lines.append(('AR', ar))
                lines.append(('CY', cy))
                continue
            if ar:
                lines.append(('AR', ar))
            continue
        if is_arabic(line) and not is_cyrillic(line):
            lines.append(('AR', line))
        elif is_cyrillic(line) and not is_arabic(line):
            lines.append(('CY', line))
        else:
            # Mixed or other — skip section headers etc.
            lines.append(('OT', line))

    # Walk and find triplets: AR → CY (tajik) → CY (russian)
    triplets = []
    i = 0
    while i < len(lines) - 2:
        kind1, val1 = lines[i]
        kind2, val2 = lines[i + 1]
        kind3, val3 = lines[i + 2]
        if kind1 == 'AR' and kind2 == 'CY' and kind3 == 'CY':
            ar = clean_arabic(val1)
            ar = ARABIC_FIXES.get(ar, ar)
            tj = clean_translation(val2)
            ru = clean_translation(val3)
            # Skip headers, titles, course-info lines
            tj_low = tj.lower()
            ru_low = ru.lower()
            is_title = (
                tj_low == 'тоҷикӣ' or 'луғати' in tj_low or 'арабӣ' in tj_low
                or 'шайх' in ru_low or 'мадина' in ru_low or 'донишгоҳи' in ru_low
            )
            # Word must be 1–8 Arabic chars (no spaces). Skip if Arabic too long (sentence)
            ar_letters = sum(1 for c in ar if ARABIC_RE.match(c))
            ok_length = 1 <= ar_letters <= 12
            if ar and tj and ru and ok_length and not is_title:
                triplets.append({"ar": ar, "tj": tj, "ru": ru})
            i += 3
            continue
        i += 1

    return triplets


if __name__ == '__main__':
    root = Path(__file__).resolve().parent.parent
    for src_name, out_name in [
        ('books_src/book2.pdf', 'words_book2.json'),
        ('books_src/book3.pdf', 'words_book3.json'),
    ]:
        src = root / src_name
        out = root / 'scripts' / out_name
        words = extract_pdf(src)
        # De-duplicate by Arabic text
        seen = set()
        unique = []
        for w in words:
            key = w['ar']
            if key not in seen:
                seen.add(key)
                unique.append(w)
        out.write_text(json.dumps(unique, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"{src_name}: extracted {len(words)} -> {len(unique)} unique entries")

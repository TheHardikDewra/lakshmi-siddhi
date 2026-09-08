# लक्ष्मी-सिद्धि — a readable edition

A public-domain Hindi tantra text, re-ordered and typeset for the web.

**Live:** https://lakshmi-siddhi.vercel.app

> **लक्ष्मी-सिद्धि** — *लक्ष्मी तन्त्र और सम्बन्धित मन्त्र साधनाओं का विशिष्ट संग्रह*
> सम्पादक: डॉ॰ चमनलाल गौतम · संस्कृति संस्थान, ख्वाजा कुतुब (वेदनगर), बरेली

## What this is

The source was a raw OCR dump: **456 loose `.txt` files**, one per scanned page,
straight from the UC Berkeley scan (Library of Congress PL-480 program, shelf
mark `UCAL $B8201`). Every page carried a running header, chapters ran into each
other, Sanskrit ślokas were shredded across lines, and the paragraphs broke
wherever the page did.

This repo turns that into a book you can actually read:

| | |
|---|---|
| Chapters | 47, in 4 sections |
| Printed pages | 9 – 448 |
| Words | ~97,700 |
| Śloka blocks | 832 |
| Section headings | 90 |

## How the order was recovered

The printed विषय-सूची is present in the scan but its page numbers are unreliable —
this OCR reads Devanagari **९** as **६** almost every time, so chapter 9's page
"६६" is really 69. So the chapter map was fixed by cross-checking three
independent signals, and only kept where all three agreed:

1. **The printed table of contents** (scans 11–12).
2. **The `N-वाँ अध्याय` headings** inside लक्ष्मी-तन्त्र — all 25 found in the body text.
3. **The running headers**, which change at every chapter break (`लक्ष्मी एकाक्षर यंत्र`
   → `लक्ष्मी चतुरक्षर यन्त्र` → …). A header first appears on the recto, so a
   chapter opening on a verso shows its header one page later — that off-by-one
   is expected and accounted for.

Printed body page **N** is always scan file **N + 4**.

## What the parser does

`tools/parse_hindi.py`

- Strips the two-line running header (`१० ]` / `[ लक्ष्मी-सिद्धि`) even when OCR
  reflows it onto one line or garbles the numerals.
- Rejoins paragraphs across page turns and de-hyphenates words broken by a line
  wrap (`डिज-` + `रायली` → `डिजरायली`).
- **Separates Sanskrit mūla from Hindi commentary.** The tell: a Hindi paragraph
  only closes on a daṇḍa at its *last* line, so two or more consecutive
  daṇḍa-closed lines mean verse. A line carrying Hindi function words
  (है, हैं, चाहिए, अर्थात्, वाला …) is never verse, even when it ends on `॥४३॥` —
  the commentary quotes the verse number too.
- Flags yantras. They are number squares; OCR flattens them into a row of loose
  digits, so the reader shows the surviving cells and says the grid was lost
  rather than passing it off as prose.

## Reader

Single static page, no build step, no framework. `data/book.json` (1.5 MB) is
fetched once and rendered client-side.

- Full-text search across every chapter, verse and heading — press <kbd>/</kbd>
- <kbd>←</kbd> <kbd>→</kbd> (or <kbd>j</kbd> <kbd>k</kbd>) move between chapters
- Original print pagination shown in the margin, so it can be cited
- Light / dark, follows the system and remembers an override

## Layout

```
index.html            the reader
data/book.json        the parsed book
tools/parse_hindi.py  OCR dump -> book.json
```

Rebuild:

```bash
python3 tools/parse_hindi.py
```

## Provenance and accuracy

The text is a faithful re-ordering of a **1970s-era OCR scan** — no words were
rewritten, dropped, or "corrected". OCR errors from the source survive in the
body text, notably Devanagari **९ ↔ ६** and stray marks in the śloka numbering.
Treat it as a reading and search copy; check the original scan before citing.

## Licence

The book itself is a public-domain scan held by UC Berkeley. The parser and
reader in this repo are MIT.

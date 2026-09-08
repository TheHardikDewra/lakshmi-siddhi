#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parse the OCR page dump of लक्ष्मी-सिद्धि (Dr. Chaman Lal Gautam,
Sanskriti Sansthan, Bareilly) into a structured, ordered book.

Source: 456 page files, UCAL_$B8201_XXXXXXXX.txt  (UC Berkeley scan)
Printed body page N  ==  scan file N + 4
"""
import json, os, re

SRC = '/Users/hardikdewra/Downloads/$b8201'
OUT = '/Users/hardikdewra/Desktop/GitHub Repos.nosync/lakshmi-siddhi/data'
OFFSET = 4
LAST_BODY_PAGE = 448            # scan 452; 453-456 are library / publisher plates

DEV2ASCII = str.maketrans('०१२३४५६७८९', '0123456789')

# ---------------------------------------------------------------- structure --
# (chapter no, title, first printed page). Cross-checked three ways: the printed
# विषय-सूची, the "N-वाँ अध्याय" headings inside लक्ष्मी-तन्त्र, and the running
# headers, which change at every chapter break.
SECTIONS = [
    ("प्रस्तावना", "चार प्रारम्भिक निबन्ध", [
        (1,  "लक्ष्मी साधना की मनोवैज्ञानिक पृष्ठभूमि", 9),
        (2,  "लक्ष्मी-नारायण पूजन और वैदिक समाजवाद", 14),
        (3,  "लक्ष्मी का आधार — अलिप्त व अनासक्त जीवन", 18),
        (4,  "समुद्र मन्थन और लक्ष्मी-सिद्धि का स्पष्टीकरण", 24),
    ]),
    ("लक्ष्मी-तन्त्र", "पच्चीस अध्याय — मूल श्लोक सहित", [
        (5,  "इन्द्र की तपस्या", 30),
        (6,  "इन्द्र-लक्ष्मी संवाद", 42),
        (7,  "त्रैगुण्य और सत्-चित् विवेचन", 56),
        (8,  "लक्ष्मी की कृपा किन पर होती है", 62),
        (9,  "सृष्टि रचना रहस्य", 69),
        (10, "आत्मज्ञान और उसकी प्राप्ति", 78),
        (11, "लक्ष्मी-मन्त्र विवेचन", 98),
        (12, "पन्द्रह दशाएँ और सप्तबीज", 107),
        (13, "मन्त्र साधन विधि", 110),
        (14, "श्रीशक्ति के दो प्रकार", 123),
        (15, "मन्त्र-कोश और मुद्रा-कोश", 130),
        (16, "अंग न्यासादिक विधि", 152),
        (17, "अन्तर्याग वर्णन", 166),
        (18, "बहिर्याग का तात्विक स्वरूप", 190),
        (19, "लक्ष्मी यजन विधान", 202),
        (20, "भोग के पदार्थ और अर्पण विधि", 216),
        (21, "अक्षमाला और होम विधि", 224),
        (22, "दीक्षा और अभिषेक विधि", 243),
        (23, "पुरश्चरण विधि", 254),
        (24, "मन्त्र विनियोग", 267),
        (25, "तारा बीज पिण्ड आदि वर्णन", 287),
        (26, "चार मूर्तियों की विधि", 300),
        (27, "व्यूह वर्णन", 307),
        (28, "जप साधन", 314),
        (29, "श्री सूक्त वर्णन", 321),
    ]),
    ("लक्ष्मी महासाधना", "बारह मन्त्र प्रयोग", [
        (30, "लक्ष्मी एकाक्षर बीज यन्त्र प्रयोग", 362),
        (31, "चतुरक्षर लक्ष्मी बीज मन्त्र प्रयोग", 367),
        (32, "दशाक्षर लक्ष्मी मन्त्र प्रयोग", 369),
        (33, "सिद्धलक्ष्मी का एकादशाक्षर प्रयोग", 372),
        (34, "द्वादशाक्षर महालक्ष्मी मन्त्र प्रयोग", 378),
        (35, "ज्येष्ठा लक्ष्मी मन्त्र प्रयोग", 385),
        (36, "वसुधा लक्ष्मी मन्त्र प्रयोग", 390),
        (37, "त्रयोविंशत्यक्षर लक्ष्मी मन्त्र प्रयोग", 395),
        (38, "सप्तविंशत्यक्षर महालक्ष्मी मन्त्र प्रयोग", 396),
        (39, "कुबेर मन्त्र प्रयोग", 400),
        (40, "पञ्चदशी काम्य प्रयोग", 404),
        (41, "कार्तवीर्य मन्त्र प्रयोग", 411),
    ]),
    ("स्तोत्र साधनायें", "छह स्तोत्र", [
        (42, "लक्ष्मी सूक्त", 416),
        (43, "लक्ष्मी कवच", 417),
        (44, "लक्ष्मी स्तोत्र", 420),
        (45, "लक्ष्मी हृदय स्तोत्र", 421),
        (46, "लक्ष्मी अष्टोत्तरशतनाम स्तोत्र", 431),
        (47, "लक्ष्मी सहस्रनाम स्तोत्र", 433),
    ]),
]

# Words that only ever appear in a running header on this scan.
HEADER_WORDS = [
    'लक्ष्मी-सिद्धि', 'लक्ष्मी सिद्धि', 'लक्ष्मी - सिद्धि', 'लक्ष्मा सिद्धि',
    'लक्ष्मा-सिद्धि', 'लक्ष्मो-सिद्धि', 'लक्ष्मो सिद्धि', 'लक्ष्मा-सिद्ध',
    'लक्ष्मी-तन्त्र', 'लक्ष्मी तन्त्र', 'लक्ष्मीतन्त्र', 'लक्ष्मी - तन्त्र',
    'लक्ष्मी तन्व', 'लक्ष्मीतन्व', 'साधना की पृष्ठभूमि', 'साधना की पृष्टभूमि',
    'साधना क पृष्ठभूमि', 'लक्ष्मी एकाक्षर यंत्र', 'लक्ष्मी एकाक्षर यन्त्र',
    'लक्ष्मी चतुरक्षर', 'दशाक्षर यन्त्र', 'दशाक्षर यंत्र', 'एकादशाक्षर यन्त्र',
    'द्वादशाक्षर मन्त्र', 'द्वादशक्षर मन्त्र', 'ज्येष्ठा लक्ष्मी मन्त्र',
    'ज्येष्टा लक्ष्मी मन्त्र', 'ज्येष्ठा लक्ष्मो मंत्र', 'वसुधा लक्ष्मी मन्त्र',
    'वसुधा लक्ष्मो मन्त्र', 'सप्तविंशत्यक्षर मंत्र', 'कुबेर मन्त्र', 'कुवेर मन्त्र',
    'पञ्चदशीकाम्य', 'पञ्चदशीक', 'पञ्चदशीकाभ्य', 'कार्तवीर्य मन्त्र',
    'स्तोत्र साधनायें', 'लक्ष्मी कवच', 'लक्ष्मी हृदय स्तोत्र',
    'लक्ष्मी - हृदय स्तोत्र', 'अष्टोत्तरशतनाम स्तोत्र', 'लक्ष्मी सहस्रनाम स्तोत्र',
    'लक्ष्मी महासाधना',
]

DIG = '[०-९0-9]'
NUMISH    = re.compile(r'^[\s\(\[\{\|\'"।:\.,१-]*(?:%s{1,3}[\s\)\]\}\|:\.,।\'"१-]*)+$' % DIG)
VERSE_NUM = re.compile(r'(?:[॥|।]{1,2}\s*%s{1,3}\s*[॥|।]{0,2}|%s{1,3}\s*[॥|]{1,2})\s*$' % (DIG, DIG))
DANDA_END = re.compile(r'[।॥|]\s*%s{0,3}\s*[।॥|]{0,2}\s*$' % DIG)
SENT_END  = re.compile(r'[।॥:?!]\s*[\'"\)\]]?\s*$')
JUNK      = re.compile(r'^[\s\W_%sa-zA-Z]{0,3}$' % DIG)
ADHYAYA   = re.compile(r'अध्याय')
NUM_HEAD  = re.compile(r'^%s{1,2}\s*[-–—.)]\s*\S' % DIG)
LABEL     = re.compile(r'^(.{2,42}?)\s*[:ः]\s*$')
GRID      = re.compile(r'^\S{1,6}(?:\s+\S{1,6}){0,2}$')
DIGIT_ONLY = re.compile(r'^[\s%s\W_]+$' % DIG)

# Function words that occur in the editor's Hindi commentary but never in the
# Sanskrit mula text. One hit is enough to rule a line out of a verse block.
HINDI_TELL = re.compile(
    'है|हैं|हुआ|हुई|हुए|नहीं|चाहिए|अर्थात|वाले|वाला|वाली|करता|करते|करना|'
    'होता|होती|होते|गया|गई|दिया|देना|तरह|प्रकार|इसलिए|जाता|जाती|रहा|रही|'
    'सकता|सकती|इसका|उसका|यहाँ|यहां|जिसका|तात्पर्य|कहते|लेकर|द्वारा')

# Short standalone labels the book uses to open a ritual step.
KNOWN_LABELS = {
    'मंत्र', 'मन्त्र', 'ध्यान', 'ध्यानः', 'विनियोग', 'प्रयोग विधि', 'यन्त्र',
    'यंत्र', 'न्यास', 'पूजन', 'फल', 'फलश्रुति', 'कवच', 'स्तोत्र',
}


def is_header_line(s):
    if not s:
        return True
    if NUMISH.match(s):
        return True
    if len(s) < 58:
        for w in HEADER_WORDS:
            if w in s:
                return True
    return False


def load_page(scan_idx):
    """Return the body lines of one scanned page, running header removed."""
    with open(os.path.join(SRC, 'UCAL_$B8201_%08d.txt' % scan_idx),
              encoding='utf-8', errors='replace') as fh:
        lines = [l.strip() for l in fh.read().split('\n')]
    lines = [l for l in lines if l]
    # The header occupies the first 1-3 physical lines but OCR sometimes
    # reflows it, so test each of the first three individually.
    keep, seen_body = [], False
    for i, l in enumerate(lines):
        if not seen_body and i < 3 and is_header_line(l):
            continue
        seen_body = True
        keep.append(l)
    while keep and JUNK.match(keep[-1]):
        keep.pop()
    return keep


def clean(s):
    s = s.replace('​', '').replace('﻿', '')
    s = re.sub(r'[\u0600-\u06ff\u0e00-\u0e7f\u4e00-\u9fff]+', '', s)
    s = re.sub(r'([:ः])(?=["“‘\'])', r'\1 ', s)
    s = re.sub(r'[ \t]+', ' ', s)
    s = re.sub(r'\s+([।॥,;])', r'\1', s)
    return s.strip()


def sanskritish(s):
    """A Sanskrit pada: short, closes on a danda, carries no Hindi function word."""
    return (len(s) < 105 and DANDA_END.search(s) is not None
            and HINDI_TELL.search(s) is None)


def classify(lines):
    """Tag every line as heading (h) / verse (v) / figure (f) / prose (p)."""
    n = len(lines)
    tag = ['p'] * n

    # 1. headings
    for i, s in enumerate(lines):
        prev_closed = (i == 0) or SENT_END.search(lines[i - 1]) is not None
        if ADHYAYA.search(s) and len(s) < 42:
            tag[i] = 'h'
        elif NUM_HEAD.match(s) and len(s) < 62 and not DANDA_END.search(s):
            tag[i] = 'h'
        elif len(s) < 46 and s.endswith('-') and i + 1 < n and prev_closed:
            tag[i] = 'h'
        elif (LABEL.match(s) and len(s) < 44 and prev_closed
              and len(s.split()) <= 5):
            tag[i] = 'h'
        elif s.rstrip('ः: ।') in KNOWN_LABELS:
            tag[i] = 'h'

    # 2. flattened yantra grids: a run of very short digit/symbol-only lines
    i = 0
    while i < n:
        if tag[i] == 'p' and GRID.match(lines[i]) and len(lines[i]) <= 12:
            j = i
            while (j < n and tag[j] == 'p' and GRID.match(lines[j])
                   and len(lines[j]) <= 12):
                j += 1
            run = lines[i:j]
            numeric = sum(1 for x in run if DIGIT_ONLY.match(x))
            if len(run) >= 4 and numeric >= len(run) / 2:
                for k in range(i, j):
                    tag[k] = 'f'
            i = j
        else:
            i += 1

    # 3. verse runs. A Hindi paragraph only closes on a danda at its *last*
    #    line, so two or more consecutive danda-closed padas means mula text.
    i = 0
    while i < n:
        if tag[i] == 'p' and sanskritish(lines[i]):
            j = i
            while j < n and tag[j] == 'p' and sanskritish(lines[j]):
                j += 1
            run = lines[i:j]
            if len(run) >= 2 or any(VERSE_NUM.search(x) for x in run):
                for k in range(i, j):
                    tag[k] = 'v'
            i = j
        else:
            i += 1
    return tag


def blockify(lines, first_pg):
    """Group tagged lines into heading / verse / paragraph blocks."""
    lines = [clean(l) for l in lines]
    lines = [l for l in lines if l and not JUNK.match(l)]
    tag = classify(lines)
    blocks, buf, mode = [], [], None

    def flush():
        nonlocal buf, mode
        if not buf:
            return
        if mode == 'v':
            blocks.append({'t': 'verse', 'v': buf[:]})
        elif mode == 'f':
            cells = [c for c in ' '.join(buf).split() if c]
            if cells:
                blocks.append({'t': 'fig', 'v': cells})
        elif mode == 'h':
            head = clean(buf[0].rstrip('-–— '))
            if head:
                blocks.append({'t': 'h', 'v': head})
        else:
            txt = ''
            for part in buf:
                if not txt:
                    txt = part
                elif txt.endswith('-'):
                    txt = txt[:-1] + part          # de-hyphenate a broken word
                else:
                    txt += ' ' + part
            blocks.append({'t': 'p', 'v': clean(txt)})
        buf, mode = [], None

    for s, t in zip(lines, tag):
        if mode and (t != mode or t == 'h'):
            flush()
        mode = t
        buf.append(s)
        if t == 'h':
            flush()
    flush()
    if blocks and first_pg is not None:
        blocks[0]['pg'] = first_pg
    return blocks


def merge_across_pages(all_blocks):
    """Rejoin a paragraph or verse that was split by a page turn."""
    out = []
    for b in all_blocks:
        prev = out[-1] if out else None
        if (prev and b['t'] == 'p' and prev['t'] == 'p'
                and not SENT_END.search(prev['v']) and 'pg' not in b):
            prev['v'] = clean(prev['v'][:-1] + b['v'] if prev['v'].endswith('-')
                              else prev['v'] + ' ' + b['v'])
            continue
        if (prev and b['t'] == 'p' and prev['t'] == 'p'
                and not SENT_END.search(prev['v'])):
            pg = b.pop('pg')
            prev['v'] = clean(prev['v'][:-1] + b['v'] if prev['v'].endswith('-')
                              else prev['v'] + ' ' + b['v'])
            prev.setdefault('cont', pg)
            continue
        out.append(dict(b))
    return out


def strip_title_lines(lines, title):
    """A chapter opens with its title set over one or two centred lines."""
    want = re.sub(r'[^ऀ-ॿ]', '', title)
    if not want:
        return lines
    got, take = '', 0
    for l in lines[:3]:
        if len(l) > 55 or SENT_END.search(l):
            break
        got += re.sub(r'[^ऀ-ॿ]', '', l)
        take += 1
        # accept once the collected head covers most of the title
        if len(got) >= len(want) * 0.6 and got[:8] == want[:8]:
            return lines[take:]
    return lines


def drop_repeated_title(blocks, num, title):
    """The chapter heading is reprinted at the top of its first page."""
    core = re.sub(r'[^ऀ-ॿ]', '', title)[:10]
    while blocks:
        b = blocks[0]
        v = b['v'] if b['t'] in ('h', 'p') else ''
        flat = re.sub(r'[^ऀ-ॿ]', '', v)
        if b['t'] == 'h' and (ADHYAYA.search(v) or NUM_HEAD.match(v)
                              or (core and core in flat)):
            blocks = blocks[1:]
            continue
        if b['t'] == 'p' and core and flat.startswith(core) and len(v) < 80:
            blocks = blocks[1:]
            continue
        break
    return blocks


TINY = re.compile(r'^[०-९0-9]{1,3}$|^[a-zA-Z]{1,2}$')
NUMTOK = re.compile(r'^[०-९0-9]{1,3}$')


def mark_scrambled_figures(blocks):
    """A yantra is a number square. OCR flattens it into a line of loose
    tokens, so any paragraph that is mostly one- and two-character tokens is
    a diagram, not prose."""
    out = []
    for b in blocks:
        if b['t'] == 'p':
            toks = [t for t in b['v'].split() if not re.fullmatch(r'[।॥|\W_]+', t)]
            if (len(toks) >= 6
                    and sum(1 for t in toks if NUMTOK.match(t)) >= 4
                    and sum(1 for t in toks if TINY.match(t)) >= len(toks) * 0.45):
                out.append({'t': 'fig', 'v': b['v'].split(), **({'pg': b['pg']} if 'pg' in b else {})})
                continue
        out.append(b)
    return out


def build_chapters():
    flat = [(n, t, p, sec[0]) for sec in SECTIONS for (n, t, p) in sec[2]]
    chapters = []
    for i, (num, title, start, sec) in enumerate(flat):
        end = flat[i + 1][2] - 1 if i + 1 < len(flat) else LAST_BODY_PAGE
        blocks = []
        for pg in range(start, end + 1):
            lines = load_page(pg + OFFSET)
            if pg == start:
                lines = strip_title_lines(lines, title)
            blocks.extend(blockify(lines, pg))
        blocks = merge_across_pages(blocks)
        blocks = drop_repeated_title(blocks, num, title)
        blocks = mark_scrambled_figures(blocks)
        if blocks:
            blocks[0]['pg'] = start
        words = 0
        for b in blocks:
            words += (sum(len(x.split()) for x in b['v'])
                      if b['t'] in ('verse', 'fig') else len(b['v'].split()))
        chapters.append({'n': num, 'title': title, 'section': sec,
                         'start': start, 'end': end,
                         'blocks': blocks, 'words': words})
    return chapters


def build_preface():
    blocks = []
    for scan in range(7, 11):
        blocks.extend(blockify(load_page(scan), None))
    blocks = merge_across_pages(blocks)
    if blocks:
        blocks[0]['v'] = re.sub(r'^\s*(BL1225|L3G38|भूमिका)\s*', '',
                                blocks[0]['v']).strip()
        blocks[0]['v'] = re.sub(r'^\s*(BL1225|L3G38|भूमिका)\s*', '',
                                blocks[0]['v']).strip()
    return [b for b in blocks if b['v'] and b['v'] not in ('भूमिका', '#')]


def main():
    chapters = build_chapters()
    book = {
        'id': 'lakshmi-siddhi',
        'title': 'लक्ष्मी-सिद्धि',
        'subtitle': 'लक्ष्मी तन्त्र और सम्बन्धित मन्त्र साधनाओं का विशिष्ट संग्रह',
        'editor': 'डॉ॰ चमनलाल गौतम',
        'editorNote': 'पूर्व सम्पादक — “जीवन-यज्ञ”, “युग-संस्कृति”',
        'publisher': 'संस्कृति संस्थान, ख्वाजा कुतुब (वेदनगर), बरेली',
        'lang': 'hi',
        'scan': 'UC Berkeley · Library of Congress PL-480 · UCAL $B8201',
        'pages': LAST_BODY_PAGE,
        'preface': {'title': 'भूमिका', 'by': 'चमनलाल गौतम',
                    'blocks': build_preface()},
        'sections': [{'title': s[0], 'note': s[1],
                      'chapters': [c[0] for c in s[2]]} for s in SECTIONS],
        'chapters': chapters,
    }
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, 'book.json')
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(book, fh, ensure_ascii=False, separators=(',', ':'))

    kinds = {}
    for c in chapters:
        for b in c['blocks']:
            kinds[b['t']] = kinds.get(b['t'], 0) + 1
    print('chapters : %d' % len(chapters))
    print('blocks   : %s' % kinds)
    print('words    : %d' % sum(c['words'] for c in chapters))
    print('json     : %.1f KB' % (os.path.getsize(path) / 1024))


if __name__ == '__main__':
    main()

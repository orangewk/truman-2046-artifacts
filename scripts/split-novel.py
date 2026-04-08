import re, sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('novel.md', encoding='utf-8') as f:
    novel_lines = f.readlines()

with open('novel-part2.md', encoding='utf-8') as f:
    part2_lines = f.readlines()

BAD_CHARS = str.maketrans({'/': '-', ':': '-', '*': '-', '?': '-', '"': '-', '<': '-', '>': '-', '|': '-', chr(92): '-'})

def safe_name(title):
    return title.translate(BAD_CHARS)

def save(filename, lines, start, end):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(''.join(lines[start:end]).strip())
    print(f'  {filename} ({end-start} lines)')

# === novel.md: 第一章 着想と設計 ===

chapters = []
current = None
for i, line in enumerate(novel_lines):
    if line.startswith('## 第'):
        if current is not None:
            chapters.append((current, i))
        current = i
if current:
    chapters.append((current, len(novel_lines)))

for idx, (s, e) in enumerate(chapters, 1):
    title = novel_lines[s].strip().lstrip('#').strip()
    # Remove "第X章: " prefix for filename, keep number
    fn = safe_name(title)
    save(f'novel/第一章 着想と設計/{idx:02d} {fn}.md', novel_lines, s, e)

# === novel-part2.md ===

lines = part2_lines

subject_line = zero79_line = afterword_line = None
for i, line in enumerate(lines):
    if '# 互換性検証レポート' in line and i > 1400 and subject_line is None:
        subject_line = i
    if line.strip() == '# 0.79' and i > 3000:
        zero79_line = i
    if '## あとがき' in line:
        afterword_line = i

print(f'subject={subject_line}, 0.79={zero79_line}, afterword={afterword_line}')

# 第二章 壁
save('novel/第二章 壁/01 壁.md', lines, 4, 151)

# 第三章 転換
save('novel/第三章 転換/01 転換.md', lines, 152, 208)

# 第四章 2046年の世界
can_docs = []
current = None
for i in range(208, subject_line):
    if lines[i].startswith('# ') and '第四部' not in lines[i]:
        if current is not None:
            can_docs.append((current, i))
        current = i
if current:
    can_docs.append((current, subject_line))

for idx, (s, e) in enumerate(can_docs, 1):
    title = lines[s].strip().lstrip('#').strip()[:40]
    save(f'novel/第四章 2046年の世界/{idx:02d} {safe_name(title)}.md', lines, s, e)

# 第五章 被験者の記録
shuushou_line = zero79_line
for i in range(max(0, zero79_line - 10), zero79_line):
    if '# 終章' in lines[i]:
        shuushou_line = i
        break

sub_docs = []
current = None
for i in range(subject_line, shuushou_line):
    if lines[i].startswith('# '):
        if current is not None:
            sub_docs.append((current, i))
        current = i
if current:
    sub_docs.append((current, shuushou_line))

for idx, (s, e) in enumerate(sub_docs, 1):
    title = lines[s].strip().lstrip('#').strip()[:40]
    save(f'novel/第五章 被験者の記録/{idx:02d} {safe_name(title)}.md', lines, s, e)

# 第六章 終話
save('novel/第六章 終話/01 0.79.md', lines, zero79_line, afterword_line)

# あとがき
save('novel/あとがき.md', lines, afterword_line, len(lines))

print('Done!')

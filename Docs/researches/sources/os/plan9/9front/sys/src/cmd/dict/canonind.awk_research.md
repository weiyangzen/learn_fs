# File Research: sources/os/plan9/9front/sys/src/cmd/dict/canonind.awk

Purpose: Converts raw dictionary index output from `mkindex` into canonical `dict` index form.

Key behavior:
- Expects exactly one raw index file argument and tab field separator.
- For each input row, fields 2..NF are words associated with offset `$1`.
- Empty words are skipped.
- Parenthesized alternates generate two entries:
  - one without the parenthesized text,
  - one with it included.
- Non-parenthesized words generate a single `word<TAB>offset` entry.
- Writes intermediate output to `junk`, sorts it uniquely by case-folded word and numeric offset, then removes `junk`.

Notable details:
- Uses old awk `sort` key syntax: `sort -u -t'\t' +0f -1 +0 -1 +1n -2`.

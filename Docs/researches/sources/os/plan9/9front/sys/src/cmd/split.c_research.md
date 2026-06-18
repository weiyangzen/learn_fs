# File Research: sources/os/plan9/9front/sys/src/cmd/split.c

`split.c` is the Plan 9 `split` command implementation. It splits input into output files either by fixed line count or by regular-expression matches.

Key responsibilities:
- Parses options: `-n`/`-l` line count, `-e` regex, `-f` output stem, `-s` suffix, `-x` skip matched separator lines, and `-i` case-insensitive matching.
- Reads from a named file or stdin using `Biobuf`.
- In line-count mode, opens a new output every `n` lines and copies trailing non-newline bytes to the last file.
- In regex mode, compiles the expression, starts output with `matchfile`, and creates a new output whenever the regex matches.
- Uses capture group 1 as the output file name when present, appending `suffix`; otherwise uses incrementing suffixes.
- Generates output names from `stem` plus two-letter suffix `aa` through `zz` in `nextfile`.
- Handles output creation and buffer switching in `openf`.
- Implements case folding for ASCII letters in `fold`.

Important interactions:
- Uses Plan 9 `regexp.h` `Reprog` and `Resub`.
- Uses Plan 9 `ARGBEGIN`, `Bopen`, `Binit`, `Brdline`, `Bwrite`, `Bterm`, `create`, and `%r` error formatting.

Notable details:
- Output suffix space is capped at `zz`; further files are not created and a warning is printed once.
- `openf` error text says `grep: can't create`, likely inherited typo.

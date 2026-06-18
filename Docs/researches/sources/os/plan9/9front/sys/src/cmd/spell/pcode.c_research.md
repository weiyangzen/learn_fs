# File Research: sources/os/plan9/9front/sys/src/cmd/spell/pcode.c

`pcode.c` converts annotated spelling word lists into the compact binary dictionary format consumed by `sprog.c`. Input lines are `word<TAB>affixcode[,affixcode...]`; output is a big-endian encoded affix table followed by sorted, prefix-compressed dictionary entries.

`main()` reads one or more input files, stores words in fixed global arrays, sorts `Dict` records by word with `qsort()`, then calls `pdict()`. `readinput()` copies each word into the global `space` buffer and converts the comma-separated code string with `typecode()`.

`typecode()` maps textual affix names (`n`, `ed`, `comp`, `nopref`, `ion`, `va`, `ms`, etc.) to the `code.h` bitmasks through small alphabet-indexed tables. Unique bit combinations are interned in `encodes[]`; dictionary entries store an index into that table rather than the full bitmask.

`pdict()` writes `ncodes`, all encoded bitmasks, and then each sorted word as a two-byte header plus suffix bytes. The header uses bit 15 as an entry marker, bits 14..11 as the number of prefix bytes shared with the previous word, and bits 10..0 as the affix-code index. All multi-byte integers are written big-endian by `sput()` and `lput()`.

Important constraints: `words`, `space`, and `encodes` are fixed-size globals with hard exits on overflow; duplicate words are reported but still encoded; unknown affix codes return code index zero after printing an error; and the binary format must remain consistent with `sprog.c`'s `readdict()` decoder.

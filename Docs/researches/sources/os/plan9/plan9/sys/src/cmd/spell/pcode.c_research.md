# File Research: sources/os/plan9/plan9/sys/src/cmd/spell/pcode.c

Compiler for annotated spelling lists into compact binary dictionaries.

Key behavior:
- Reads lines of `word<TAB>affixcode[,affixcode...]`.
- Maps named affix codes to bit masks from `code.h`.
- Interns distinct bit-mask combinations in `encodes[]`.
- Sorts words alphabetically.
- Emits a big-endian binary dictionary: number of code masks, code masks, then prefix-compressed word entries.

Important details:
- Fixed arrays allow up to 200000 words, 500000 bytes of word storage, and 4094 distinct encodings.
- Word entries store affix-code index plus count of common prefix bytes with the previous word.
- Reports word/space/code counts and output byte count on stderr.

Filesystem relevance:
- Direct dictionary file generator; reads source word lists and writes binary dictionary to stdout.

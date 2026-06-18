# File Research: sources/os/plan9/plan9/sys/src/cmd/spell/sprog.c

Runtime spelling checker and affix analyzer.

Key behavior:
- Loads compressed dictionaries from `/sys/lib/amspell`, `/sys/lib/brspell`, or `-f file`.
- Reads words from stdin and prints words not accepted by the dictionary/affix rules.
- Supports British spelling mode, OCR/correction classification modes, verbose derivation output, x/debug lookup output, and Acme-style id prefixes.
- Tests dictionary words directly, then recursively strips prefixes and suffixes according to large prefix/suffix tables.
- Uses affix bit masks to decide whether a base word can accept a transformation.

Important details:
- Dictionary lookup uses a two-character index table into decompressed word storage.
- Suffix tables are stored reversed, matching from the word end.
- Derivation messages are accumulated for verbose output.
- `ise()` Britishizes relevant suffix rules by replacing `z` with `s`.
- Ordinal numbers such as `21st` and `12th` are accepted specially.

Filesystem relevance:
- Direct: reads binary spelling dictionary files from `/sys/lib` or a caller-supplied path.

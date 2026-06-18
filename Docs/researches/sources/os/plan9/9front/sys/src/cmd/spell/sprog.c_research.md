# File Research: sources/os/plan9/9front/sys/src/cmd/spell/sprog.c

`sprog.c` is the runtime spelling checker and affix analyzer. It reads the compact dictionary produced by `pcode.c`, then checks words from standard input by direct dictionary lookup plus recursive prefix and suffix stripping rules.

The file is table-driven. Large `Suftab` tables encode reversed suffix patterns, transformation routines, messages, required affix flags, and allowed follow-on classes. `Ptab` tables define allowed prefixes. The transformation functions (`strip`, `cstrip`, `s`, `es`, `an`, `ize`, `y_to_e`, `i_to_y`, `ily`, `bility`, `subst`, `tion`, `CCe`, `VCe`) mutate candidate word endings, check phonetic/vowel constraints, and recursively call `trypref()` or `trysuff()`.

`main()` parses spell options, loads `/sys/lib/amspell` or `/sys/lib/brspell`, then processes each input line. It handles optional acme-style `file:addr:word` prefixes, preserves or lowers case depending on the original word, skips numeric ordinals, and prints either misspellings, correction markers, or verbose derivation traces. `-b` Britishises `z` suffix rules through `ise()`/`ztos()`, `-c`/`-C` produce compact correctness codes, `-v` records derivations, `-x` traces dictionary lookups, and `-f` selects the dictionary file.

Dictionary lookup is optimized around the binary format. `readdict()` reads the big-endian affix table, expands prefix-compressed dictionary bytes into `space`, and builds `spacep[]`, an index by the first two 7-bit characters. `dict()` uses that two-character bucket and a binary search over compressed entries; found entries return the decoded affix bitmask.

Important behavior: prefix stripping refuses `NOPREF` words and validates `in-`/`im-`/`ir-`/`un-` semantics through `inun()`. Derivation recording uses fixed `deriv[]` and `affix[]` buffers. The dictionary buffer sizes are fixed and must match the encoder’s expected limits. Many routines temporarily mutate `word[]`, so recursive paths rely on careful restoration of changed characters.

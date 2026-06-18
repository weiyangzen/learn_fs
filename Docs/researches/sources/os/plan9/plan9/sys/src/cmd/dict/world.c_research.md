# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/world.c

Implements callbacks for “Languages of the World” dictionary files, including mixed single-byte text plus embedded Japanese JIS and Chinese GB2312 sequences.

Records begin with three big-endian 16-bit lengths: headword, pronunciation, and definition. `worldprintentry` skips the header, limits output to the headword length for `cmd == 'h'`, and streams bytes through `putchar` unless raw mode is requested.

`chartab` maps 256 single-byte codes to Unicode runes, including Latin, phonetic, Greek, and special symbols. `putchar` maintains a small state machine: UTF/single-byte mode, Kana/JIS high-byte mode, GB high-byte mode, and low-byte completion. Bytes `0xfe` and `0xff` enter Japanese or GB multibyte modes; `S2J`, `tabjis208`, and `tabgb2312` convert encoded pairs to runes. Unknown or control bytes become `\xx` escapes when not otherwise used for shift controls.

`worldnextoff` seeks to `fromoff - 1`, reads the three lengths, and returns the next record offset as `fromoff - 1 + 6 + nh + np + nd`. The comment notes callers must pass `<address of valid entry> + 1`.

Integration points: registered for several bilingual dictionaries in `utils.c`; depends on `kuten.h`, `jis208.c`, and `gb2312.c` tables.

Risks and notes: offset convention is unusual and must match the main dictionary/index code. Unrecognized multibyte pairs degrade to byte escapes. The state variable `xflag` is local and always zero in the visible code, leaving some `NONE` branches effectively unreachable for escaped emission.

# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/conv_gbk.c

GBK input/output converter for `tcs`.

Key functions:
- `gbkproc` treats bytes `>= 0x80` as lead bytes, combines lead/trail into a 16-bit code, and looks up `tabgbk[code - GBKMIN]` when within range.
- `gbk_in` streams input through the state machine.
- `gbk_out` builds a reverse table over `GBKMIN..GBKMAX`, emits ASCII below `0x80`, and emits two-byte GBK for mapped runes.

Notable behavior:
- Reverse table initialization writes `tab[tabgbk[i-GBKMIN]] = i` without checking for `-1`, assuming the table/range is suitable.
- Unmapped output emits `BYTEBADMAP` unless `clean` suppresses it.

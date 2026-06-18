# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/conv_jis.c

Implements Japanese JIS-family decoders and encoders for ISO-2022-JP, Shift-JIS, EUC-JP, and a permissive guessing mode.

Key points:
- Includes `kuten208.h`, `kuten212.h`, and `jis.h`.
- Defines four decoder state machines:
  - `alljis`: permissive decoder that handles ISO-2022 escape shifts, 7-bit/8-bit JIS, and Shift-JIS-like pairs.
  - `ms`: Shift-JIS/MS-Kanji decoder with half-width katakana mapping to `0xFEC0 + c`.
  - `ujis`: EUC-JP decoder for JIS X 0208 and JIS X 0212 codeset 3; codeset 2 is reported unsupported.
  - `jis`: stricter ISO-2022-JP/JIS-kanji decoder.
- Escape handling recognizes `ESC $ @`, `ESC $ B`, and `ESC ( J/H/B`, including Japanese Roman mode where backslash maps to Yen and tilde maps to spacing macron.
- Kuten indices are computed from byte pairs and resolved through `tabkuten208` or `tabkuten212`; negative table entries are treated as ambiguous mappings and emitted after sign removal with a warning.
- EOF in the middle of a two-byte sequence is handled by warning and synthesizing a low byte.
- `do_in` centralizes the buffered input loop for all four decoders.
- Exposes `jis_in`, `ujis_in`, `msjis_in`, and `jisjis_in`.
- `tab_init` builds the shared reverse table from `tabkuten208`, using absolute values for ambiguous entries.
- `jisjis_out` emits ISO-2022-JP escape shifts into and out of JIS mode.
- `msjis_out` converts kuten bytes to Shift-JIS using `J2S`.
- `ujis_out` emits EUC-JP bytes by OR-ing both bytes with `0x80`.

Dependencies and interactions:
- Uses conversion macros such as `CANS2J`, `S2J`, and `J2S` from `jis.h`.
- Registered by `tcs.c` under `jis`, `jis-kanji`, `iso-2022-jp`, `ms-kanji`, and `ujis`.

Research relevance:
- Most complex converter in this group; it encodes the stateful Japanese charset handling in `tcs`.

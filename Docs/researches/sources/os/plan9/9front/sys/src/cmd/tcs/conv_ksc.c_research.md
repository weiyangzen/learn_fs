# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/conv_ksc.c

Implements Korean EUC/KSC 5601 decoding and encoding.

Key points:
- Credits contribution by Teruhiko Kurosaka.
- Defines `SS2` and `SS3`, but support for codesets 2 and 3 is commented out; only codesets 0 and 1 are used.
- `ukscproc` maps ASCII directly, except backslash maps to Unicode Won sign `0x20A9` when `korean646` is enabled.
- Non-ASCII bytes start a two-byte KSC 5601 sequence; the ordinal is `((lead & 0x7f) - 33) * 94 + ((trail & 0x7f) - 33)`.
- Invalid or unknown KSC values increment `nerrors`, optionally warn, and emit `BADMAP` unless `clean` is set.
- `uksc_in` follows the standard buffered decoder pattern.
- `uksc_out` lazily builds the shared reverse table from `tabksc5601`, respecting negative ambiguous entries by indexing their absolute Rune value.
- Mapped output Runes are encoded as two EUC bytes by OR-ing row/cell values with `0x80`.

Dependencies and interactions:
- Includes `ksc.h` for `tabksc5601` and `ksc5601max`.
- Registered by `tcs.c` as `euc-k`.

Research relevance:
- Runtime converter for Korean EUC/KSC handling in `tcs`.

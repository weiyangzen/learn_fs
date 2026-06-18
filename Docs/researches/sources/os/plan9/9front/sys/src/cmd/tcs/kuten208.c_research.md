# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/kuten208.c

## Purpose
Defines the JIS X 0208 kuten-to-Unicode mapping table used by JIS, EUC-JP, and Shift-JIS converters.

## Key Elements
Includes `kuten208.h` and defines `long tabkuten208[KUTEN208MAX]`. The table has 8407 entries, matching `KUTEN208MAX`, indexed by the converter formula `hi * 100 + lo - 3232` after byte normalization.

Entries map JIS X 0208 kuten positions to Unicode code points. `-1` marks unmapped positions. Some entries are negative in the table family convention used by `conv_jis.c` to signal ambiguous mappings, though in this file the observed negative sentinel is `-1`.

## Dependencies
Declared in `kuten208.h`. Used by `conv_jis.c` for:
- `alljis`, `ms`, `ujis`, and `jis` input decoding.
- reverse-table initialization in `tab_init`.
- `jisjis_out`, `msjis_out`, and `ujis_out`.
Also referenced by `font/kmap.c` for font mapping generation.

## Behavior/Risks
This is pure data, but it is a critical shared table for multiple Japanese encodings. Input converters treat out-of-range indexes or `-1` entries as conversion errors. Output converters build a reverse `tab[]` by scanning all `KUTEN208MAX` entries, so duplicate Unicode mappings resolve to whichever table position is assigned last during the scan.

Any off-by-one change to `KUTEN208MAX` or row order would affect ISO-2022-JP, EUC-JP, and Shift-JIS behavior together.

## Verification
Read completely: 1055 lines, 59960 bytes. SHA-256: `08089fb28a6c852380cab4f5be938ee289689dfb47b9726f57c20dae13399f93`.

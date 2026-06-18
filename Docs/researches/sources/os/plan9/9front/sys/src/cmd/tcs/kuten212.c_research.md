# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/kuten212.c

## Purpose
Defines the JIS X 0212 kuten-to-Unicode mapping table used for EUC-JP codeset 3 input.

## Key Elements
Includes `kuten212.h` and defines `long tabkuten212[KUTEN212MAX]`. The table has 7768 entries, matching `KUTEN212MAX`, indexed in `conv_jis.c` with the same kuten-style `hi * 100 + lo - 3232` formula for codeset 3 byte pairs.

The table maps JIS X 0212 positions to Unicode and uses `-1` for unmapped slots.

## Dependencies
Declared in `kuten212.h`. Used by `conv_jis.c` only on EUC-JP input when codeset 3 is selected by byte `0x8f`; there is no corresponding output path in this code for JIS X 0212.

## Behavior/Risks
This is input-only table data for supplementary Japanese characters. Invalid codeset 3 byte ranges are rejected before lookup; valid but unmapped kuten positions produce conversion errors and `BADMAP` unless clean mode suppresses replacement output.

Because there is no reverse output table for `tabkuten212`, characters decoded from JIS X 0212 may not round-trip back through the available JIS output encoders.

## Verification
Read completely: 975 lines, 55407 bytes. SHA-256: `3361e421d5a4dd2aa2131b0b652912c7de89d4e102cfe5b897cfdebe8af88c4f`.

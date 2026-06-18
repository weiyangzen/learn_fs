# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/kuten212.h

## Purpose
Defines the fixed size and extern declaration for the JIS X 0212 kuten mapping table.

## Key Elements
Defines `KUTEN212MAX` as `7768` and declares `extern long tabkuten212[KUTEN212MAX];`.

## Dependencies
Included by `kuten212.c` and `conv_jis.c`.

## Behavior/Risks
No include guard is present. The constant must stay synchronized with `tabkuten212` and with the bounds checks in the EUC-JP codeset 3 decoder.

## Verification
Read completely: 3 lines, 94 bytes. SHA-256: `afe90feb0cc7ec20cd2913acea35e772f0a584ebf1ec08b31d8cd4db2390316a`.

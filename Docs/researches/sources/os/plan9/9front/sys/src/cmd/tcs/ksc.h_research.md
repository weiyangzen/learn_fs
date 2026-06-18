# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/ksc.h

## Purpose
Declares the KS C 5601 mapping table and its logical entry count for Korean conversion code.

## Key Elements
Exports:
- `extern long tabksc5601[];`
- `extern int ksc5601max;`

The comments state the table is indexed by kuten-style code position and that `ksc5601max` is the number of usable entries.

## Dependencies
Included by `ksc.c`, which defines the objects, and `conv_ksc.c`, which consumes them.

## Behavior/Risks
No include guard is present. The header contains only extern declarations, so repeated inclusion is not a storage-definition problem, but it relies on conventional single-definition behavior from `ksc.c`.

## Verification
Read completely: 2 lines, 112 bytes. SHA-256: `28b62139f19ffd46d9831973e95d3c95f6fd2b3cc34698bd3eafa8e90ce09440`.

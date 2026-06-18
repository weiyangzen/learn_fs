# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/ksc.h

## Purpose

`ksc.h` declares the KSC 5601 mapping table and its usable length for Korean conversion code.

## Contents

- `extern long tabksc5601[];`
- `extern int ksc5601max;`

Both are defined in `ksc.c`.

## Integration

`conv_ksc.c` includes this header to access the forward and reverse mapping source for Korean EUC/KSC conversion. The comments state that the table is indexed by kuten-style positions.

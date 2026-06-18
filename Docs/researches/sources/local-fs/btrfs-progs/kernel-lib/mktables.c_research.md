# File Research: sources/local-fs/btrfs-progs/kernel-lib/mktables.c

## Purpose
Build-time generator for RAID-6 Galois-field lookup tables.

## Key Flow
- `gfmul(a, b)` performs GF(2^8) multiplication with polynomial reduction `0x1d`.
- `gfpow(a, b)` computes powers modulo the 255-element nonzero field cycle.
- `main()` prints C definitions for:
  - `raid6_gfmul[256][256]`
  - `raid6_vgfmul[256][32]`
  - `raid6_gfexp[256]`
  - `raid6_gfinv[256]`
  - `raid6_gfexi[256]`

## Integration
Generated output is consumed by RAID6 recovery/generation code declared in `raid56.h` and used in `raid56.c`.

## Risks
- Generator output is deterministic but large; build integration must ensure generated tables match the declarations’ alignment/type expectations.
- No argument handling is needed; any command-line arguments are ignored.

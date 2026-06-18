# File Research: sources/windows/winbtrfs/src/galois.c

## Purpose

`galois.c` implements finite-field arithmetic used by WinBtrfs RAID-6 parity generation and recovery.

## Core Data

- `glog[]`: exponent-to-field-value lookup table for GF(2^8).
- `gilog[]`: inverse log lookup table mapping field values to exponents.

These tables support fast multiply/divide by converting operations into exponent arithmetic modulo 255.

## Entry Points

- `galois_divpower(uint8_t* data, uint8_t div, uint32_t len)`: divides every byte in a buffer by `2^div`.
- `gpow2(uint8_t e)`: returns `2^e` in the field.
- `gmul(uint8_t a, uint8_t b)`: multiplies two GF(2^8) elements, returning zero if either operand is zero.
- `gdiv(uint8_t a, uint8_t b)`: divides two GF(2^8) elements; returns `0xff` for divide-by-zero as a should-not-happen sentinel.
- `galois_double(uint8_t* data, uint32_t len)`: multiplies every byte by 2 using the RAID-6 primitive polynomial reduction constant `0x1d`.

## Implementation Details

- `galois_double()` has 64-bit fast path on AMD64/ARM64 and 32-bit fast path elsewhere.
- Wide-word doubling masks high bits and applies `0x1d` reduction per byte.
- Remaining bytes are processed individually.
- Comments credit H. Peter Anvin's "The mathematics of RAID-6" for the derived algorithm.

## Dependencies

- Includes `btrfs_drv.h`.
- Called from RAID/parity paths in read, write, scrub, and flush-thread code.

## Research Notes

- This file is small but critical for RAID-6 correctness. Arithmetic mistakes here would affect parity reconstruction and scrub repair.
- No allocation or locking occurs here; callers own buffer lifetime and synchronization.
- There is a `FIXME - SIMD?` note, indicating known optimization headroom for parity-heavy workloads.

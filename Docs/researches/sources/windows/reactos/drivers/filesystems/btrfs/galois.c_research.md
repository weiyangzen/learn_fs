# File Research: sources/windows/reactos/drivers/filesystems/btrfs/galois.c

## Purpose

`galois.c` implements Galois-field arithmetic helpers used by the Btrfs driver, primarily for RAID-6 style parity math. The comments identify the doubling logic as derived from H. Peter Anvin’s “The mathematics of RAID-6”.

## Data Tables

`glog` is the exponent/log-to-value table for GF(2^8).

`gilog` is the inverse value-to-log table.

Both tables are fixed 256-byte lookup tables.

## Functions

`galois_divpower(uint8_t* data, uint8_t div, uint32_t len)` divides each nonzero byte in a buffer by `2^div` using the log tables. Zero bytes remain zero.

`gpow2(uint8_t e)` returns `2^e` in the field, using modulo 255 exponent wraparound.

`gmul(uint8_t a, uint8_t b)` multiplies two field elements; either zero operand returns zero.

`gdiv(uint8_t a, uint8_t b)` divides field elements. Division by zero returns `0xff` as a “should not happen” sentinel; zero numerator returns zero.

`galois_double_mask64` or `galois_double_mask32` builds a byte mask for bytes with the high bit set, used by fast doubling.

`galois_double(uint8_t* data, uint32_t len)` multiplies every byte in the buffer by two in GF(2^8), using 64-bit chunks on AMD64/ARM64, 32-bit chunks elsewhere, then a byte tail. Reduction uses `0x1d`.

## Research Notes

This is compact arithmetic support code. It has no allocation or external side effects. The only architectural sensitivity is the direct 64-bit/32-bit casting of `uint8_t*` buffers, which assumes unaligned accesses are acceptable on the target build/runtime.

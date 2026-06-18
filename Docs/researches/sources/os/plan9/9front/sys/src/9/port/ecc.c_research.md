# File Research: sources/os/plan9/9front/sys/src/9/port/ecc.c

Implements NAND flash ECC generation and correction for 256-byte data chunks. `nandecc` uses a precomputed table to compute line and column parity into a 24-bit ECC value.

`nandecccorrect` compares calculated and stored ECC values. It returns good on exact match, corrects a single data-bit error when the syndrome matches `CORRECTABLEMASK`, updates stored ECC, detects a single-bit error in the ECC itself, or reports an uncorrectable two-bit error. Optional reporting prints calculated/stored ECC and correction details.

The file depends on `nandecc.h` for `NandEccError` result values.

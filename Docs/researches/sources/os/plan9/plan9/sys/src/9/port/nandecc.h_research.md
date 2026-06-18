# File Research: sources/os/plan9/plan9/sys/src/9/port/nandecc.h

Purpose: Public NAND ECC interface for `ecc.c`.

Contents:
- Defines `NandEccError` values: bad, good, corrected one-bit data error, and corrected one-bit ECC error.
- Declares `nandecc` for 256-byte buffers.
- Declares `nandecccorrect` for checking/correcting a 256-byte buffer given calculated and stored ECC plus optional reporting.

Dependencies and integration:
- Used by NAND flash code that needs ECC generation and correction.

# File Research: sources/os/plan9/plan9/sys/src/9/port/ecc.c

Purpose: NAND flash ECC calculation and correction for 256-byte data chunks.

Key logic:
- `nandecc` computes a 24-bit ECC using a 256-entry lookup table and line/parity accumulation.
- `nandecccorrect` compares calculated and stored ECC, detects no error, correctable one-bit data error, one-bit ECC error, or uncorrectable multi-bit error.
- Correctable data errors flip the identified byte/bit and update the stored ECC.

Dependencies and integration:
- Includes `nandecc.h`; intended for NAND flash drivers and flash filesystem code.

Risks and notes:
- Corrects only single-bit data errors or single-bit ECC-storage errors.
- Optional reporting prints diagnostic details.

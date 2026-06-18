# File Research: sources/os/plan9/9front/sys/src/9/port/nandecc.h

NAND ECC public declarations.

Key contents:
- Defines `NandEccError` values for bad ECC, good ECC, one-bit data correction, and one-bit ECC correction.
- Declares `nandecc()` over a 256-byte buffer.
- Declares `nandecccorrect()` with calculated/stored ECC and report-bad control.

Role:
- Shared header for NAND flash ECC generation and correction code.

# File Research: sources/local-fs/mtd-utils/flash_otp_write.c

## Purpose
Writes raw stdin data into user OTP storage at a requested offset.

## Key Elements
Selects user OTP mode, queries MTD geometry, seeks to the offset, reads stdin in write-size chunks for NAND or 256-byte chunks otherwise, pads partial NAND writes with `0xff`, and writes until EOF.

## Dependencies
Uses `common.h`, `mtd/mtd-user.h`, and `mtd_type_is_nand_user`.

## Behavior/Risks
Destructive and irreversible at the bit level: OTP bits set to 0 cannot be erased. It uses a fixed 2048-byte buffer and errors if NAND writesize exceeds it.

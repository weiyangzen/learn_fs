# File Research: sources/local-fs/mtd-utils/flash_otp_dump.c

## Purpose
Dumps factory or user One-Time Programmable MTD data as hexadecimal rows.

## Key Elements
Accepts `-f` or `-u`, opens the device read-only, selects `MTD_OTP_FACTORY` or `MTD_OTP_USER` with `OTPSELECT`, and reads/prints 16 bytes per line.

## Dependencies
Uses MTD OTP ioctls from `mtd/mtd-user.h`.

## Behavior/Risks
Read-only utility. Return values are errno-style integers, and the printed offset is relative to the selected OTP data stream.

# File Research: sources/local-fs/mtd-utils/flash_otp_info.c

## Purpose
Reports factory or user OTP region count, offsets, sizes, and lock state.

## Key Elements
Selects OTP mode, queries region count with `OTPGETREGIONCOUNT`, allocates a stack VLA of `struct otp_info`, then queries and prints all regions.

## Dependencies
Uses `mtd/mtd-user.h` OTP ABI.

## Behavior/Risks
Read-only, but uses a variable-length stack array sized by kernel-reported count. Error message for `OTPGETREGIONINFO` incorrectly says `OTPGETREGIONCOUNT`.

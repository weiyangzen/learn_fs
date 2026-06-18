# File Research: sources/local-fs/mtd-utils/flash_otp_lock.c

## Purpose
Locks a user OTP range permanently.

## Key Elements
Requires `-u <device> <offset> <size>`, selects user OTP mode, parses offset/size with `strtoul`, prompts for confirmation, and issues `OTPLOCK`.

## Dependencies
Uses `mtd/mtd-user.h` and `common.h` for prompting.

## Behavior/Risks
Irreversible operation. The tool warns that locked OTP regions cannot be unlocked but relies on the caller to provide exact region boundaries.

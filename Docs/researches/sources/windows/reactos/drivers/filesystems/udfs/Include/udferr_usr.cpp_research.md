# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/udferr_usr.cpp

## Purpose
Defines the formatter/checker error-code-to-message table.

## Main Contents
- `mkudf_err_msg[]` maps `MKUDF_*` and `CHKUDF_*` codes to user-facing English messages.
- Includes generated/adjacent entries from `udferr_usr_cpp.h`.
- Ends with sentinel `{0xffffffff, "Unknown error"}`.

## Coverage
Messages cover format success, invalid parameters, hardware layout/read/write failures, descriptor write failures, VAT/session constraints, blank/format requirements, ISO image errors, bad-block/system-area failures, privilege issues, user abort, and checker mount failure.

## Notes
The table contains historical spelling mistakes in messages, which may be user-visible compatibility artifacts.

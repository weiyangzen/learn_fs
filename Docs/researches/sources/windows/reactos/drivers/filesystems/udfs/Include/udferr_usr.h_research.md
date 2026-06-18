# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/udferr_usr.h

## Purpose
Declares formatter/checker error codes, the error-message table shape, and fallback NT-like status constants for non-native builds.

## Main Contents
- Defines `MKUDF_OK`, a large range of failing `MKUDF_*` status values, `MKUDF_PENDING`, and `CHKUDF_CANT_MOUNT`.
- Includes `udferr_usr_h.h` for additional generated/adjacent error definitions.
- Defines `struct err_msg_item` and declares `mkudf_err_msg[]`.
- If `STATUS_SUCCESS` is not already defined, supplies many NTSTATUS-style constants used by shared user/kernel code.

## Notes
`STATUS_SUCCESS` is defined as `1` in the fallback block, unlike normal NTSTATUS `0`. Code using this fallback should rely on local success macros/semantics rather than assuming Windows kernel values.

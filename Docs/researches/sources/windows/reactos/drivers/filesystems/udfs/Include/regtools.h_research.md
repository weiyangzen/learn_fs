# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/regtools.h

## Purpose
Declares the multi-environment registry helper API.

## Main Contents
- Includes `check_env.h`.
- Maps `HKEY` to `HANDLE` outside `WIN_32_MODE`.
- Declares `RegTGetKeyHandle`, `RegTCloseKeyHandle`, `RegTGetDwordValue`, and `RegTGetStringValue`.

## Notes
This header abstracts registry access enough for shared UDFS kernel/user support code, but still exposes Windows-specific types and calling conventions.

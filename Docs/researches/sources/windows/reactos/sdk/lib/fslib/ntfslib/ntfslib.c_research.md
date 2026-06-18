# File Research: sources/windows/reactos/sdk/lib/fslib/ntfslib/ntfslib.c

This file is a placeholder NTFS filesystem library implementation.

Core behavior:
- Includes user-mode NDK types and FMIFS definitions.
- `NtfsFormat` is marked `UNIMPLEMENTED` and returns `TRUE`.
- `NtfsChkdsk` is marked `UNIMPLEMENTED`, sets `*ExitStatus` to `STATUS_SUCCESS`, and returns `TRUE`.

Risk points:
- Both public entry points report success despite doing no work.
- Callers cannot distinguish “not implemented” from a successful format/check by return value.
- Parameters are unused and no media validation, locking, formatting, or checking is performed.

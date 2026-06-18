# File Research: sources/windows/dokany/dokan/setfile.c

Implements file information mutation dispatch for allocation size, basic info, disposition, EOF, rename, and valid data length.

Key helpers:
- `DokanSetAllocationInformation`: calls `SetAllocationSize`.
- `DokanSetBasicInformation`: calls `SetFileAttributes`, then `SetFileTime`.
- `DokanSetDispositionInformation`: interprets classic and extended disposition structures, checks read-only attributes when possible, sets `DeletePending`, and calls `DeleteFile` or `DeleteDirectory`.
- `DokanSetEndOfFileInformation`: calls `SetEndOfFile`.
- `DokanSetRenameInformation`: copies the variable-length new name to a null-terminated buffer and calls `MoveFile`.
- `DokanSetValidDataLengthInformation`: delegates to `SetEndOfFile`.

`DispatchSetInformation`:
- Allocates result buffer for rename cases so the new name can be echoed back.
- Switches on `FileInformationClass`.
- Reports delete-pending state for successful disposition requests.
- Copies rename target into result buffer on successful rename.
- Completes through `EventCompletion`.

Important behavior:
- `FilePositionInformation` is intentionally left to the driver and returns `STATUS_NOT_IMPLEMENTED`.
- Unknown information classes leave `STATUS_INVALID_PARAMETER`.
- Deletion is rejected as `STATUS_CANNOT_DELETE` for read-only files when attributes can be queried.

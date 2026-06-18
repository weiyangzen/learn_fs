# File Research: sources/windows/winfsp/src/sys/ea.c

Purpose:
Implements extended-attribute query and set IRP handling for WinFsp filesystem volume devices. It validates EA buffers, serves cached EA data when available, posts query/set EA transactions to user mode, updates file-node EA cache and metadata, and emits EA change notifications.

Major entry points and roles:
- `FspQueryEa` and `FspSetEa` are major dispatch routines for `IRP_MJ_QUERY_EA` and `IRP_MJ_SET_EA`, routing only fsvol devices to internal handlers.
- `FspFsvolQueryEa` validates EA support and file-object state, tries to serve the query from the file-node EA meta cache, otherwise buffers the user output, creates `FspFsctlTransactQueryEaKind`, stores the file-node owner in request context, and posts to the I/O queue.
- `FspFsvolQueryEaComplete` validates user-mode response EA data, releases the asynchronous file-node owner, reacquires the file node, attempts to populate/reference the EA cache, copies matching EA records into the caller buffer, and returns the resulting EA status.
- `FspFsvolSetEa` buffers and validates the originating process EA input, creates `FspFsctlTransactSetEaKind`, copies the EA input into the request buffer, and posts to user mode with full file-node ownership.
- `FspFsvolSetEaComplete` updates file info from the response, validates optional returned EA data, refreshes or invalidates the cached EA buffer, increments `EaChangeCount`, reports a `FILE_NOTIFY_CHANGE_EA` modification, releases ownership, and completes successfully.

EA copy behavior:
- `FspFsvolQueryEaCopy` chooses between name-list query mode (`EaList` supplied) and index scan mode.
- `FspFsvolQueryEaGetCopy` iterates caller-supplied `FILE_GET_EA_INFORMATION` records, ignores duplicate requested names, validates EA names, searches the source `FILE_FULL_EA_INFORMATION` list case-insensitively, and emits either the matching EA or a zero-length placeholder value for missing names.
- `FspFsvolQueryEaIndexCopy` implements restart/index/single-entry enumeration. It advances from one-based EA indexes, copies aligned `FILE_FULL_EA_INFORMATION` records, updates `FileDesc->EaIndex`, and returns Windows EA statuses such as `STATUS_NO_MORE_EAS`, `STATUS_NO_EAS_ON_FILE`, `STATUS_NONEXISTENT_EA_ENTRY`, `STATUS_BUFFER_TOO_SMALL`, and `STATUS_BUFFER_OVERFLOW`.
- Case preservation is controlled by `VolumeParams.CasePreservedExtendedAttributes`; when disabled, copied EA names are uppercased in place with `FspEaNameUpcase`.

Cache and consistency:
- Cached EA data is referenced through `FspFileNodeReferenceEa` and released via `FspFileNodeDereferenceEa`.
- Query completion validates filesystem-provided EA buffers with `FspEaBufferFromFileSystemValidate`; this validator may alter the buffer, so response buffers are treated as mutable.
- Index-based scans detect stale enumeration state: if no restart/index flag is present and the file-node `EaChangeCount` differs from `FileDesc->EaChangeCount`, the query returns `STATUS_EA_CORRUPT_ERROR`.
- Set completion increments `FileNode->EaChangeCount`, so existing EA enumerations can detect mutation.

Validation and buffer handling:
- Originating-process set buffers are validated with `FspEaBufferFromOriginatingProcessValidate` before being sent to user mode.
- Filesystem-returned EA buffers are validated before caching or copying.
- Query output uses `FspBufferUserBuffer` for buffered write access; set input uses buffered read access.
- Copy routines compute record sizes from `FIELD_OFFSET(FILE_FULL_EA_INFORMATION, EaName) + name length + null byte + value length` and align output advancement with `FSP_FSCTL_ALIGN_UP(..., sizeof(ULONG))`.

Dependencies:
- Uses declarations and macros from `sys/driver.h`, especially `FSP_NEXT_EA`, file-node/file-desc APIs, I/O request APIs, and EA validation helpers.
- Uses Windows EA structures: `FILE_GET_EA_INFORMATION`, `FILE_FULL_EA_INFORMATION`, query/set EA stack parameters, and EA-specific NTSTATUS values.
- Depends on WinFsp user-mode transaction kinds `FspFsctlTransactQueryEaKind` and `FspFsctlTransactSetEaKind`.

Research notes:
- The critical invariants are EA-list structural validation, aligned traversal, case-insensitive matching, and correct distinction between caller-provided invalid EA names versus filesystem-returned inconsistent EA lists.
- The query completion path has a subtle cache branch: if cache insertion is not needed or not possible, it safely copies directly from the response buffer.
- Set EA deliberately accepts an invalid or absent returned EA buffer by invalidating the EA cache, while still using returned file info and completing the set operation successfully.

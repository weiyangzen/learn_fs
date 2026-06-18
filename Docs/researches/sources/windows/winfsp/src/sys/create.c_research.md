# File Research: sources/windows/winfsp/src/sys/create.c

Large `IRP_MJ_CREATE` implementation for WinFsp control, virtual, and volume devices. This is the core namespace/open path.

Top-level dispatch:
- `FspFsctlCreate()` recognizes volume-control opens by prefix and calls `FspVolumeCreate`; otherwise succeeds as `FILE_OPENED`.
- `FspFsvrtCreate()` succeeds as `FILE_OPENED`.
- `FspFsvolCreate()` handles volume file opens and wraps the main flow with the file-rename resource unless the open is a recursive main-file open.

ECP handling:
- Detects WinFsp main-file-open ECP to avoid deadlocking on rename resource.
- Optionally fixes reparse-point case damage from an undocumented reparse ECP.
- For WSL features, detects atomic-create ECP and accepts reparse-buffer creation data.

Create validation/building:
- Rejects unsupported file-id opens, paging-file opens, conflicting directory/non-directory options, invalid temp directory creates, invalid EA usage, invalid atomic-create inputs, and root operations that cannot be created/overwritten/superseded/deleted.
- Aligns allocation size to volume allocation unit.
- Normalizes doubled leading backslashes.
- Builds absolute path from related file object plus relative file name or validates absolute path.
- Validates stream syntax and optionally opens the main file for named streams.
- Strips volume prefix when mounted below a prefix.
- Tracks trailing backslash and stream type.
- Allocates `FSP_FILE_NODE`, `FSP_FILE_DESC`, and user-mode create request.
- Copies optional security descriptor and EA/reparse extra buffer into request.
- Populates create request with options, attributes, allocation size, desired/granted/share access, privilege flags, case sensitivity, named-stream offset, and security-descriptor acceptance flag.

Prepare phase:
- For create requests, duplicates the subject token into a user-mode impersonation-token handle, stores process for later close, and passes token handle plus originating process id in request.
- For overwrite requests, acquires full file-node lock, performs oplock processing, checks `MmCanFileBeTruncated`, purges cache, and marks request ownership.

Completion phase:
- Handles user-mode failures and `STATUS_REPARSE`.
- Reparse handling supports:
  - `IO_REMOUNT`,
  - device-absolute paths,
  - symbolic-link reparse buffers, including device-relative symlinks that are prefixed with volume name/prefix,
  - generic reparse buffers copied to IRP auxiliary buffer.
- Populates file node and descriptor from create response.
- Handles normalized names for case-insensitive file systems, requiring response normalized name to differ only by case.
- Calls `FspFileNodeOpen()` with additional access for overwrite/supersede share checks.
- On sharing violation, may break oplocks and retry.
- Sets access state, file object contexts, section object pointer, VPB, temporary flag, and cache support.
- For normal opens, calls `FspFsvolCreateTryOpen()` to acquire main lock, process oplocks, update metadata/security if safe, flush image sections for write/delete opens, and send create notifications.
- For overwrite/supersede, converts the request into an `Overwrite` transaction, validates hidden/system attribute rules, and posts best-effort.

Cleanup/finalizers:
- `FspFsvolCreatePostClose()` posts a best-effort close to user mode after failed local open completion.
- `FspFsvolCreateRequestFini()` releases extra file nodes, descriptors, token handles, process refs, and rename ownership.
- Try-open and overwrite finalizers back out oplocks, post close if needed, close file nodes, dereference, and release rename ownership.

Oplock logic:
- `FspFsvolCreateSharingViolationOplock()` mimics FastFat behavior for sharing violations, reposting to worker context when waiting may be needed.
- Handles main-file and stream sharing violations across alternate data streams.
- `FspFsvolCreateOpenOrOverwriteOplock()` checks oplock keys, async breaks when multiple handles exist, and supports `FILE_OPEN_REQUIRING_OPLOCK`.
- Async prepare/complete helpers bridge oplock completion back into create retry paths.

Key role in architecture:
- Bridges Windows create/open semantics to WinFsp’s user-mode transaction model while preserving kernel object lifetime, share access, reparse behavior, named streams, WSL atomic create, oplocks, cache coherency, and security token propagation.

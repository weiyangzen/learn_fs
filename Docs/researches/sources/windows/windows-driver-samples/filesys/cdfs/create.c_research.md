# File Research: sources/windows/windows-driver-samples/filesys/cdfs/create.c

CDFS create/open implementation for volume, file, directory, relative, name-based, and file-ID opens.

Key responsibilities:
- Implements `CdCommonCreate`, the common FSD/FSP create path.
- Rejects unsupported create modes: paging file opens, target-directory opens, EAs, true create operations, and Win7+ `FILE_OPEN_REQUIRING_OPLOCK`.
- Normalizes and stores full names in the file object with `CdNormalizeFileNames`.
- Handles volume DASD opens, open-by-file-ID, prefix-table matches, path-table directory traversal, short-name lookup, and final directory scans.
- Creates or finds FCBs and inserts prefix entries for exact-case and case-insensitive lookup.
- Completes user opens through `CdCompleteFcbOpen`, including access checks, oplock checks, share access, CCB creation, file-object setup, cache flags, and reference/cleanup count updates.

Important behavior:
- CDFS is read-only for normal file creation semantics: only `FILE_OPEN` and `FILE_OPEN_IF` are accepted for existing files/directories/volumes.
- Empty name plus no file ID is treated as a volume open and acquires the VCB exclusively.
- `CdNormalizeFileNames` handles double leading backslashes, trailing backslashes, related file objects, open-by-ID validation, wildcard rejection, and retry behavior through `IRP_CONTEXT_FLAG_FULL_NAME`.
- Directory discovery primarily uses the ISO path table; file discovery uses directory enumeration. A directory found in a directory scan but absent from the path table is treated as disk corruption.
- Short-name matches are supported by decoding embedded short-name offsets and then resolving back to long-name/path-table state when needed.
- `CdOpenByFileId` reconstructs parent directory state from encoded path-table and dirent offsets, validating offsets against path-table and directory-stream bounds.
- `CdCompleteFcbOpen` expands `MAXIMUM_ALLOWED`, handles exclusive volume-lock opens by purging and forcing delayed closes, checks batch/exclusive oplocks, checks share access, and assigns `FO_CACHE_SUPPORTED` or `FO_NO_INTERMEDIATE_BUFFERING`.

Dependencies:
- Depends on CDFS FCB table, prefix table, path table, directory enumeration contexts, file-ID encoding helpers, CCB allocation, VCB/FCB locking, oplock callbacks, share-access APIs, and volume purge/close-drain support.
- Uses `try/finally` cleanup heavily to release FCBs, VCBs, compound path entries, and file contexts across normal, pending, and exceptional exits.

Notable risks:
- The file is lock-order sensitive: it often references an FCB under the VCB lock, drops the VCB, acquires the FCB, then reacquires the VCB to adjust references.
- File-object name buffers are mutated and may be reallocated; retry correctness depends on `IRP_CONTEXT_FLAG_FULL_NAME`.
- Open-by-ID trusts encoded offsets only after explicit validation; malformed media can otherwise drive unusual path-table and directory scans.

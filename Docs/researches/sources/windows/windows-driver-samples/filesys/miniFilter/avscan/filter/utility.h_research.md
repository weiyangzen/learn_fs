# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/utility.h

Kernel-private utility header for allocation tags, file references, generic table entries, filesystem-cache support checks, allocation wrappers, metadata helper prototypes, resource wrappers, and a safe list iteration macro.

Key definitions:
- Pool tags for strings, resources, events, and table entries.
- `AV_FILE_REFERENCE`: union supporting NTFS-style 64-bit IDs and ReFS 128-bit IDs.
- `AV_INVALID_FILE_REFERENCE` and `AV_SET_INVALID_FILE_REFERENCE`.
- `AV_GENERIC_TABLE_ENTRY`: file ID, infected state, and CSVFS revision numbers cached per instance.
- `FS_SUPPORTS_FILE_STATE_CACHE`: true for NTFS, CSVFS, and ReFS.
- Inline alloc/free helpers for nonpaged `ERESOURCE` and `KEVENT`.
- Inline resource acquire/release wrappers that enter/leave critical regions and assert IRQL/resource state.
- `LIST_FOR_EACH_SAFE` for deletion-safe list traversal.

Declared interfaces:
- Generic table callbacks: `AvCompareEntry`, `AvAllocateGenericTableEntry`, `AvFreeGenericTableEntry`.
- Metadata helpers: `AvGetFileId`, `AvGetFileSize`, `AvGetFileEncrypted`.
- `AvExceptionFilter`.

Dependencies:
- Windows kernel pool/resource/list/generic table APIs and file ID types.

Research notes:
- The resource wrappers enforce passive/APC-level usage assumptions made by the pageable callback paths.
- The cache entry stores CSVFS revision numbers alongside infection state so cache hits can remain coherent across CSVFS revision checks.

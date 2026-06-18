# File Research: sources/windows/reactos/drivers/filesystems/ntfs/fcb.c

Read status: complete file, 784 lines.

This file owns NTFS FCB creation, lookup, reference management, cache-map initialization, path traversal, alternate data stream parsing, and FCB attachment to file objects.

Key entry points:
- `NtfsCreateFCB()` and `NtfsDestroyFCB()` allocate/free FCBs and initialize resources/path/stream fields.
- `NtfsFCBIsDirectory()`, `NtfsFCBIsReparsePoint()`, `NtfsFCBIsCompressed()`, `NtfsFCBIsEncrypted()`, and `NtfsFCBIsRoot()` classify FCBs.
- `NtfsGrabFCB()`, `NtfsReleaseFCB()`, `NtfsAddFCBToTable()`, and `NtfsGrabFCBFromTable()` manage the VCB FCB list under a spin lock.
- `NtfsFCBInitializeCache()` creates a stream file object and initializes the cache map for an FCB.
- `NtfsMakeRootFCB()` and `NtfsOpenRootFCB()` construct/cache the root directory FCB.
- `NtfsMakeFCBFromDirEntry()` builds an FCB from a file record and filename attribute.
- `NtfsAttachFCBToFileObject()` allocates a CCB and attaches FCB/CCB/cache state to a caller file object.
- `NtfsDirFindFile()` resolves one directory element, including `name:stream` and `name:stream:$DATA` handling.
- `NtfsGetFCBForFile()` walks an absolute path component by component.
- `NtfsReadFCBAttribute()` reads a named attribute into a newly allocated buffer.

Important dependencies:
- Directory lookup: `NtfsLookupFileAt`.
- Attribute and record helpers: `ReadFileRecord`, `FindAttribute`, `ReadAttribute`, `GetBestFileNameFromRecord`, `GetStandardInformationFromRecord`.
- Cache manager: `CcInitializeCacheMap`, `CcUninitializeCacheMap`.

Notable behavior and risks:
- Directory FCBs are retained in the FCB table even when refcount reaches zero; non-directory FCBs are destroyed.
- FCB table lookup is case-insensitive and has a FIXME for comparing short names.
- `NtfsDirFindFile()` can return early on missing named stream without freeing the loaded file record.
- Path buffers are fixed at `MAX_PATH`; several paths rely on asserts or manual length checks.

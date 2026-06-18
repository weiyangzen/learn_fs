# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/filter/utility.c

Utility implementation for generic table callbacks and file metadata queries. It backs the per-instance file-state cache and provides helpers used by create/scan logic.

Key responsibilities:
- `AvCompareEntry` compares cached file-state entries by 128-bit file reference, lower 64 bits first and upper 64 bits second.
- `AvAllocateGenericTableEntry` and `AvFreeGenericTableEntry` allocate/free AVL table entries from paged pool.
- `AvGetFileId` queries ReFS file IDs with `FileIdInformation` and other file systems with `FileInternalInformation`, normalizing into `AV_FILE_REFERENCE`.
- `AvGetFileSize` queries `FileStandardInformation.EndOfFile`.
- `AvGetFileEncrypted` queries `FileBasicInformation.FileAttributes`.
- `AvExceptionFilter` allows expected NTSTATUS exceptions, especially while touching user buffers.

Dependencies:
- Filter Manager `FltQueryInformationFile`, `FltGetFileSystemType`, generic table callbacks, file-information classes, and structures from `utility.h`.

Research notes:
- ReFS support is handled explicitly because ReFS uses 128-bit file IDs.
- The compare function does not implement a bytewise 128-bit order, but it is self-consistent, which is sufficient for the AVL table.

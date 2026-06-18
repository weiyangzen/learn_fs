# File Research: sources/windows/dokany/dokan/volume.c

Handles volume information queries and default volume/free-space callbacks.

Key behavior:
- Default disk space: 1 GiB total, 512 MiB available/free.
- Default volume information:
  - volume name `DOKAN`;
  - serial `0x19831116`;
  - max component length `256`;
  - flags for case sensitivity/preservation, remote storage, and Unicode;
  - filesystem name `NTFS`.
- `DokanGetVolumeInformation` calls user callback if present, otherwise default.
- Implements query handlers for:
  - `FileFsVolumeInformation`
  - `FileFsSizeInformation`
  - `FileFsAttributeInformation`
  - `FileFsFullSizeInformation`
- Size handlers convert bytes to allocation units using `DokanOptions->AllocationUnitSize` and `SectorSize`.
- `DispatchQueryVolumeInformation` allocates the result buffer and dispatches by `FsInformationClass`.

Risks and notes:
- Buffer truncation is handled for string-style results; attribute info returns `STATUS_BUFFER_OVERFLOW` if the filesystem name is truncated.
- Default filesystem identity is NTFS-like even though backing semantics are supplied by user code.

# File Research: sources/virtualization/libblockdev/src/plugins/fs/f2fs.h

Declares F2FS feature flags, info data, and libblockdev F2FS operations.

Key contents:
- Defines `BDFSF2FSFeature` bit flags mirroring F2FS superblock feature bits such as encryption, zoned block support, quota, verity, and checksum features.
- Defines `BDFSF2FSInfo` with `label`, `uuid`, `sector_size`, `sector_count`, and `features`.
- Declares copy/free helpers.
- Declares mkfs, check, repair, info, resize, and label validation APIs.

Important invariants:
- `sector_count` and resize sizes use F2FS sectors.
- The feature field is a raw bitmask exposed to callers.
- Existing-device label and UUID setters are intentionally absent.

Filesystem/block relevance:
- Exposes F2FS metadata and operation APIs to the generic filesystem layer.

Notable risks:
- Feature enum values must stay aligned with upstream `f2fs_fs.h`.

# File Research: sources/virtualization/libblockdev/src/plugins/fs/udf.h

Declares UDF info data and operations.

Key contents:
- Defines `BDFSUdfInfo` with label, UUID, revision, logical volume ID, volume ID, block size, block count, and free blocks.
- Declares copy/free helpers.
- Declares mkfs, set/check label, set/check UUID, and get-info APIs.

Important invariants:
- UDF check, repair, and resize APIs are absent.
- UDF exposes both user-facing label/UUID and lower-level UDF identifiers.

Filesystem/block relevance:
- Exposes UDF metadata management and creation to the generic filesystem layer.

Notable risks:
- The UUID checker declaration has a harmless extra space before `const`.

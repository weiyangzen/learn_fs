# File Research: sources/virtualization/libblockdev/src/plugins/fs/ext.h

Declares the public ext2/ext3/ext4 API surface used by the libblockdev filesystem plugin.

Key contents:
- Defines shared `BDFSExtInfo` with `label`, `uuid`, `state`, `block_size`, `block_count`, and `free_blocks`.
- Typedefs `BDFSExt2Info`, `BDFSExt3Info`, and `BDFSExt4Info` to the same struct.
- Declares copy/free helpers for each typedef.
- Declares mkfs, check, repair, label, UUID, info, resize, and minimum-size APIs for ext2, ext3, and ext4.

Important invariants:
- The three ext family info types are ABI-distinct by name but structurally identical.
- Callers own returned info structs and must free them with the matching free helper.
- All operational functions accept `GError **` and return GLib-style success/failure values.

Filesystem/block relevance:
- This header exposes ext-family block filesystem management operations to generic dispatch and external users.

Notable risks:
- Because all ext info types alias one struct, future ext-version-specific fields would require ABI care.

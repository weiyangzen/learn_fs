# File Research: sources/local-fs/xfsprogs/db/sb.c

Implements `xfs_db` superblock field decoding and the `sb`, `uuid`, `label`, and `version` commands.

Key responsibilities:
- Registers commands for selecting allocation-group superblocks, reading/writing filesystem UUIDs, reading/writing labels, and displaying/updating selected version bits.
- Defines the superblock field table, including conditional metadata-directory and realtime-group fields.
- Reads and validates superblocks with magic/version/in-progress checks.
- Checks log cleanliness before UUID-changing operations and clears the log with the new UUID.
- Updates all AG superblocks, and realtime superblock label/UUID when present.
- Handles metauuid feature transitions when changing/restoring UUIDs on CRC filesystems.
- Prints feature names from the mounted superblock state.

Important behavior:
- Mutating commands require non-readonly expert mode.
- UUID writes refuse filesystems needing repair and require a clean log.
- `uuid rewrite`, `uuid restore`, `uuid nil`, explicit UUIDs, and generated UUIDs are supported.
- Label writes truncate to `XFSLABEL_MAX`, and `--`, `""`, or `''` mean empty label.
- `version` supports legacy feature enabling for `extflg`, `log2`, `attr1`, `attr2`, and `projid32bit`; V5 mutation is mostly blocked.
- Printing UUID/label checks all AG backup superblocks and warns on mismatch.

Dependencies:
- Uses libxfs superblock conversion, version helpers, log recovery/clear helpers, realtime superblock helpers, and global debugger state.
- Depends on `mp`, `x`, `iocur_top`, `typtab`, `expert_mode`, and `exitcode`.

Notable risks:
- These commands intentionally mutate filesystem identity and feature fields; misuse can make a filesystem inconsistent.
- `get_sb` has early returns after `push_cur`; several error paths do not `pop_cur`, relying on command process behavior rather than strict local cleanup.
- `version_f` explicitly documents incomplete V5 feature support.

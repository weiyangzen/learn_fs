# File Research: sources/local-fs/xfsprogs/db/dquot.c

Purpose: defines quota record field metadata and implements the `dquot` command for navigating to a quota record by id.

Key behavior:
- Registers `dquot [-g|-p|-u] id`, defaulting to user quotas.
- Defines `dqblk_hfld`, `dqblk_flds`, and `disk_dquot_flds`.
- Quota field tables expose disk quota magic, version, type, id, block/inode/realtime hard and soft limits, usage counters, timers, warning counters, CRC, LSN, and UUID.
- `dqtype_to_inode` loads the quota inode for user/group/project quotas, including metadir parent handling when `xfs_has_metadir` is set.
- `dquot_f` validates the requested quota type/id, maps quota id to quota file block and record offset, navigates through the quota inode bmap, sets current type to `TYP_DQBLK`, marks the buffer as a dquot buffer, offsets the current view to the specific record, and adds it to the ring.
- `xfs_dquot_set_crc` updates the CRC for the currently selected dquot record.
- `dquot_init` registers the command.

Interactions:
- Uses libxfs quota inode loading, quota path naming, transactions, inode references, and bmap lookup.
- Field types are registered by `field.c`.
- CRC command and write paths can use the dquot CRC setter.

Risks/notes:
- If the quota id maps to an unmapped quota file block, the command reports no quota data.
- CRC update asserts that the current buffer is marked as a dquot buffer.

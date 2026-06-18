# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/ext3_jbd.h

This header connects ext3 metadata operations to the JBD journaling layer.

Major content:
- `EXT3_JOURNAL(inode)` accessor.
- Transaction credit constants for single data updates, xattrs, data operations, delete operations, max transaction data, reserve blocks, and htree index operations.
- Quota-aware transaction credit macros, with no-op definitions when quota is disabled.
- Prototypes for inode dirtying and inode write reservation.
- Wrapper prototypes and macros for JBD access: undo/write/create access, revoke, dirty metadata, forget, dirty data, start/stop, extend/restart, current handle, blocks per page, force commit.
- Data-mode decision helpers: `ext3_should_journal_data`, `ext3_should_order_data`, `ext3_should_writeback_data`.

Role:
- Preserves Linux ext3 journaling call structure while allowing ReactOS/Ext2Fsd wrapper functions to add diagnostics and status conversion.

Notable constraints:
- Several helpers rely on `test_opt`, `EXT3_I`, and JBD functions being present and semantically compatible.
- Non-regular files default to journaled data in `ext3_should_journal_data`.

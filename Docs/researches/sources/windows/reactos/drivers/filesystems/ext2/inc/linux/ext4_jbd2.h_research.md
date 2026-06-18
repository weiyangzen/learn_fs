# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/ext4_jbd2.h

This header defines ext4-facing journal wrapper declarations over the JBD layer.

Major APIs:
- `ext4_journal_abort_handle`
- `__ext4_handle_dirty_super`
- `__ext4_journal_get_write_access`
- `__ext4_forget`
- `__ext4_journal_get_create_access`
- `__ext4_handle_dirty_metadata`
- `__ext4_journal_start_sb`
- `__ext4_journal_stop`

Macros:
- Wrap access/forget/dirty/start/stop calls while passing source line and an Ext2Fsd `icb` context.
- `ext4_journal_start` routes through `__ext4_journal_start`.
- `ext4_journal_extend` is a stub returning `0`.

Role:
- Lets ext4 extent/xattr code follow Linux call patterns while carrying ReactOS request context for error handling and metadata writes.

Notable constraint:
- `ext4_journal_extend` does not actually reserve more credits, so callers expecting Linux JBD2 extension semantics may not get real transaction growth.

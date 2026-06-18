# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/ext4/ext4_jbd2.c

This file supplies minimal ext4 journal helper stubs so Linux-derived ext4 extent code can compile and run in this driver. It does not implement full JBD2 transaction semantics.

`__ext4_journal_start_sb` returns the address of a static `handle_t no_journal`; `__ext4_journal_stop` returns success. Abort, write-access, create-access, forget/revoke, and dirty-super helpers are no-ops returning success. `__ext4_handle_dirty_metadata` is the meaningful exception: it marks the supplied buffer head dirty with `extents_mark_buffer_dirty`.

The practical effect is that extent metadata code follows the structure of journal-aware ext4 routines, but durability is delegated to normal dirty-buffer/writeback paths rather than real JBD2 transaction ordering. This is important context for any correctness work in the ext4 extent path: journal calls preserve call-site shape, not full journaling behavior.

# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/journal-head.h

This header defines JBD per-buffer journal metadata.

Key definitions:
- `tid_t`: transaction ID type.
- `transaction_t`: forward declaration of compound transaction.
- `struct journal_head`: back-pointer to `buffer_head`, reference count, journal list type, modified flag, frozen and committed data copies, owning/current transactions, transaction-list links, checkpoint transaction, and checkpoint-list links.

Role:
- Extends buffer heads with journal ownership and checkpoint metadata.
- Used heavily by JBD transaction, commit, revoke, and checkpoint logic.

Locking notes:
- Comments document expected protection by `jbd_lock_bh_journal_head`, `jbd_lock_bh_state`, and journal list locks.

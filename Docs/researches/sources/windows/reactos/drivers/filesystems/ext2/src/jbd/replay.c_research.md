# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/jbd/replay.c

## Scope
Ports substantial Linux JBD journal core support into the ReactOS Ext2 tree: abort/error handling, journal-head cache management, log block allocation, journal initialization/loading/wiping, superblock feature negotiation/update, transaction buffer-list management, buffer forget/release, and JBD module cache startup/shutdown.

## Key Elements
- Commit request helpers `__log_start_commit()` and `log_start_commit()` set `j_commit_request` and wake the commit waitqueue.
- Abort helpers record `JFS_ABORT`, preserve `j_errno`, optionally update the journal superblock, and expose `journal_abort()`, `journal_errno()`, `journal_clear_err()`, and `journal_ack_err()`.
- Journal-head helpers allocate, attach, grab, put, and remove `struct journal_head` objects from buffer heads while managing `BH_JBD`, `b_private`, `b_jcount`, and buffer references.
- `journal_next_log_block()`, `journal_bmap()`, and `journal_get_descriptor_buffer()` allocate logical journal blocks and map inode-backed or external journal blocks to physical block numbers.
- `journal_init_common()` initializes waitqueues, mutexes, locks, commit interval, abort-by-default state, and revoke tables.
- `journal_init_inode()` creates an inode-backed journal, allocates write buffers, maps the journal superblock, and stores `j_superblock`.
- `journal_load()` loads the superblock, validates feature bits, invokes recovery, resets dynamic journal state, clears abort, and marks the journal loaded.
- `journal_wipe()`, `journal_update_format()`, `journal_update_superblock()`, and `journal_reset()` manage on-disk superblock format and dynamic log head/tail fields.
- Transaction-list helpers file/unfile buffers across `BJ_Metadata`, `BJ_Forget`, `BJ_LogCtl`, `BJ_Reserved`, and related lists.
- `journal_forget()` removes a buffer from current journaling state, preserves checkpoint dependencies through `BJ_Forget`, and drops buffer references.
- Module init/exit creates and destroys revoke, journal-head, and handle caches.

## Dependencies
Depends on Linux JBD headers/types, revoke initialization from `revoke.c`, recovery from `recovery.c`, buffer-head operations from `linux.c`, endian and transaction helper macros, journal superblock definitions, and Ext2 inode block mapping through `bmap()`.

## Behavior/Risks
- This file is named `replay.c` but functions as a broad JBD journal core subset, not only replay.
- Many full Linux JBD runtime paths are compiled out or stubbed compared with a complete kernel JBD implementation, especially commit-thread/checkpoint destruction sections.
- `journal_load()` always calls recovery before `journal_reset()`, then writes the superblock as clean/current.
- `journal_bmap()` aborts the journal on failed inode mapping, making inode-backed journal block mapping a critical dependency.
- Journal-head lifetime depends on paired buffer references; misuse can leak or prematurely release cached buffer heads.

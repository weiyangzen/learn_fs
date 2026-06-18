# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/jbd/revoke.c

## Scope
Implements JBD revoke support: hash-table allocation, runtime revoke/cancel logic, commit-time revoke descriptor writing, recovery-time revoke insertion/testing, and revoke cleanup.

## Key Elements
- Defines `jbd_revoke_record_s` for block-number plus transaction sequence records and `jbd_revoke_table_s` for power-of-two hash tables.
- `journal_init_revoke_caches()` and `journal_destroy_revoke_caches()` manage slab caches for revoke records and tables.
- `journal_init_revoke()` allocates two revoke tables so runtime and committing/recovery state can be switched.
- `journal_revoke()` marks a block revoked, optionally finds a cached buffer head, sets revoke bits, calls `journal_forget()` for supplied buffers, and inserts the revoke record.
- `journal_cancel_revoke()` removes a pending revoke when the block is journaled again and clears revoke state on buffer aliases.
- `journal_switch_revoke_table()` flips the active revoke table for a new transaction.
- `journal_write_revoke_records()` serializes revoke records into JBD revoke descriptor blocks and frees records after writing.
- `journal_set_revoke()`, `journal_test_revoke()`, and `journal_clear_revoke()` provide recovery-time revoke table operations.

## Dependencies
Depends on JBD transaction handles, journal locks, buffer-head revoke state bits, journal descriptor allocation from `replay.c`, `journal_forget()`, list helpers, kmem cache shims, endian conversion, and transaction ID comparison helpers.

## Behavior/Risks
- Revokes prevent stale journal metadata from overwriting newer data after block deletion/reuse.
- A later journaled write in the same transaction cancels an earlier revoke, while a later revoke must dominate earlier logged data.
- Runtime commit code is inside `#ifdef __KERNEL__`; the ReactOS build depends on how its compatibility headers define this path.
- `insert_revoke_hash()` retries allocation when `journal_oom_retry` is enabled, yielding until memory becomes available.
- Recovery stores only the latest revoke sequence per block and skips replay when the logged transaction is not newer than that revoke.

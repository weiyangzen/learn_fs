# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/dmu_tx.h

Read status: complete, 153 lines.

Purpose: private DMU transaction structure definitions and DMU-internal transaction APIs.

Key structures and APIs:
- `dmu_tx_t` stores hold list, objset/dir/pool, assigned TXG, last snapshot/tried TXGs, TXG handle, temp reservation cookie, needed assignment hold, callbacks, sync-placeholder flag, netfree flag, start time, dirty wait/delay flags, and error.
- `dmu_tx_hold_type` enumerates hold kinds: new object, write, bonus, free, zap, space, spill.
- `dmu_tx_hold_t` records per-hold dnode, space/memory refcounts, type, and arguments.
- `dmu_tx_callback_t` stores commit/abort callback entries.
- Public APIs are redeclared from `dmu.h`; SPA-only and DMU-only helpers include `dmu_tx_create_assigned()`, `dmu_tx_create_dd()`, `dmu_tx_is_syncing()`, `dmu_tx_private_ok()`, `dmu_tx_add_new_object()`, `dmu_tx_dirty_buf()`, and `dmu_tx_hold_space()`.

Important implementation constraints:
- A transaction is handled by one thread, so `dmu_tx_t` itself needs no synchronization.
- `DMU_TX_DIRTY_BUF` is active only in debug builds.

Dependencies: DMU, TXG, refcount, dsl pool/dir/dnode/dbuf forward declarations.

Research notes:
- This header exposes the internal accounting model behind public transaction holds.

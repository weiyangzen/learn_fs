# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zil_impl.h

Defines private ZIL implementation structures for log write blocks, commit waiters, intent transaction grouping, async transaction trees, vdev flush tracking, and the `zilog_t` state object.

Key elements:
- `lwb_state_t` models log write block lifecycle: closed, opened, issued, write done, flush done.
- `lwb_t` stores block pointer, buffer, write/root zios, allocation tx, max txg, waiter list, vdev flush tree, and timing.
- `zil_commit_waiter_t` coordinates `zil_commit()` completion with condition variable, lock, LWB pointer, done flag, and zio error.
- `itxs_t`, `itxg_t`, and `itx_async_node_t` organize sync and async intent transactions per txg.
- `zil_vdev_node_t` tracks vdevs requiring cache flush after log writes.
- `zilog_t` holds locks, pool/spa/objset pointers, sequencing, suspend/replay flags, issuer lock, logbias/sync policy, parse statistics, per-txg intent lists, LWB list, BP tree, dirty linkage, and previous block sizes.

Main dependencies and interactions:
- Includes `zil.h` and DMU objset internals.
- Private to ZIL implementation and sync/commit paths.

Implementation notes:
- Comments precisely define lock ownership: `zl_issuer_lock` protects pre-issue LWB transitions; `zl_lock` protects completion transitions.
- `ZIL_MAX_LOG_DATA`, `ZIL_MAX_WASTE_SPACE`, and `ZIL_MAX_COPIED_DATA` tune immediate vs deferred write logging behavior.

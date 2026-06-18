# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rds/rdsib_buf.h

This legacy RDS-over-IB buffer header defines send/receive buffer states, buffer objects, buffer pools, and pool-management APIs.

Core definitions:
- Send buffer states: free, pending, error.
- Receive buffer states: free, posted, on socket queue.
- `rds_buf_t` links buffers to endpoints, SGL data segments, state, and receive free callbacks.
- `rds_bufpool_t` tracks lock-protected buffer-pool sizing, busy/free counts, free list head/tail, memory backing, CV waiters, and polling state used when interrupts are disabled.
- Global data/control receive pools are declared.

API surface:
- Initialize/free receive caches and per-endpoint send/receive pools.
- Allocate/free generic buffers, send buffers, and receive buffers.
- Test whether endpoint send/receive queues are empty.

Risk-sensitive invariants:
- Pool counts, free lists, and busy counts must stay consistent under `pool_lock`.
- `pool_cv`, waiter count, and `pool_sqpoll_pending` are only used in polling/no-interrupt mode.
- Receive buffers use `frtn_t` for STREAMS `esballoc()` ownership.

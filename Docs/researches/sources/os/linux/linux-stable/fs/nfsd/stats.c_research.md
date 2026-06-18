# File Research: sources/os/linux/linux-stable/fs/nfsd/stats.c

## Summary
Implements `/proc/net/rpc/nfsd` statistics output and proc registration.

## Main APIs
- `nfsd_proc_stat_init()`.
- `nfsd_proc_stat_shutdown()`.
- `nfsd_show()` via `DEFINE_PROC_SHOW_ATTRIBUTE(nfsd)`.

## Behavior
The proc reader prints reply-cache hits/misses/nocache, stale filehandle count, read/write byte counters, current thread count, deprecated histogram/read-ahead placeholders, generic SunRPC service stats, and when NFSv4 is enabled, per-operation NFSv4 counters plus write-delegation GETATTR count.

## State and Synchronization
Counters are per-net `percpu_counter` values in `struct nfsd_net`. Thread count uses global `nfsd_th_cnt`. Generic RPC stats are emitted through `svc_seq_show()`.

## Risks
The output format is long-standing user ABI, including deprecated zero fields. Reordering or removing fields can break monitoring tools. Counter sums are snapshots and are not intended to be transactionally consistent.

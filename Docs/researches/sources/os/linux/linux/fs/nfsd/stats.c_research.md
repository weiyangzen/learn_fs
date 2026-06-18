# File Research: sources/os/linux/linux/fs/nfsd/stats.c

## Summary
Implements procfs output for NFSD statistics under `/proc/net/rpc/nfsd` and registers/unregisters the per-net proc stats endpoint.

## Main Responsibilities
- Formats reply cache, filehandle stale, I/O byte, thread count, deprecated thread histogram, and deprecated read-ahead cache statistics.
- Delegates generic RPC service statistics formatting to `svc_seq_show()`.
- Emits per-NFSv4 operation counters and write-delegation GETATTR counter when NFSv4 is enabled.
- Registers and unregisters the proc entry through SunRPC stats helpers.

## Key Data Structures and Interfaces
- `nfsd_show()` reads `struct nfsd_net` from proc inode data and prints counter values from `nn->counter`.
- `DEFINE_PROC_SHOW_ATTRIBUTE(nfsd)` creates proc operations.
- `nfsd_proc_stat_init()` calls `svc_proc_register()`.
- `nfsd_proc_stat_shutdown()` calls `svc_proc_unregister()`.

## Important Behavior
Output preserves legacy field groups even for deprecated stats by printing zero-filled placeholders. This maintains compatibility with userspace parsers expecting historical `/proc/net/rpc/nfsd` layout.

Counter reads use `percpu_counter_sum_positive()` to aggregate per-CPU counters without exposing negative transient values.

## Dependencies
Depends on seq_file, SunRPC stats, proc/net namespace infrastructure, NFSD counters, and NFSv4 operation constants when enabled.

## Risks and Subtleties
The text format is a userspace ABI. Removing deprecated zero fields or changing ordering can break monitoring tools.

# File Research: sources/os/linux/linux/fs/nfsd/stats.h

## Summary
Declares NFSD proc stats setup/teardown and inline helpers for updating per-net and per-export NFSD counters.

## Main Responsibilities
- Exposes proc stats registration functions.
- Provides inline increment/add/subtract helpers for reply cache hits, misses, no-cache events, stale filehandles, I/O bytes, payload misses, and duplicate reply cache memory usage.
- Mirrors selected per-net stats into per-export stats when export stats are available.
- Provides an NFSv4-only helper for write delegation GETATTR conflicts.

## Key Data Structures and Interfaces
- Helpers update `nn->counter[NFSD_STATS_*]`.
- Per-export mirror updates use `exp->ex_stats->counter[EXP_STATS_*]`.
- Counter IDs come from `uapi/linux/nfsd/stats.h`.

## Important Behavior
The stale filehandle and I/O helpers update both namespace-wide and export-specific counters, allowing global proc stats and per-export reporting to stay consistent.

Duplicate reply cache memory helpers use add/sub wrappers around per-cpu counters to track allocation changes.

## Dependencies
Depends on NFSD UAPI stats IDs, Linux percpu counters, `struct nfsd_net`, and export stats structures.

## Risks and Subtleties
Callers should use these helpers instead of touching counters directly when export-level mirroring matters. Passing a null export is supported for namespace-only accounting.

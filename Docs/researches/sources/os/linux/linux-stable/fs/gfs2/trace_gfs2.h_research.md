# File Research: sources/os/linux/linux-stable/fs/gfs2/trace_gfs2.h

## Scope

This tracepoint header defines the `gfs2` trace system. It covers glock state transitions and queueing, demote requests, lock timing statistics, log pin/flush/reservation/AIL events, block mapping and iomap operations, block allocation/free state, and multi-block reservation events.

## Trace Events And Helpers

- Symbol helpers map DLM states to readable names, bitmap states to `free/used/dinode/unlinked`, reservation actions to delete/tree-delete/insert/claim, and glock flags to compact flag strings.
- `glock_trace_state()` converts GFS2 lock states to DLM trace state constants.
- Locking events: `gfs2_glock_state_change`, `gfs2_glock_put`, `gfs2_demote_rq`, `gfs2_promote`, `gfs2_glock_queue`, `gfs2_glock_lock_time`.
- Journal/log events: `gfs2_pin`, `gfs2_log_flush`, `gfs2_log_blocks`, `gfs2_ail_flush`.
- Mapping/allocation events: `gfs2_bmap`, `gfs2_iomap_start`, `gfs2_iomap_end`, `gfs2_block_alloc`, `gfs2_rs`.

## Captured State

Lock tracepoints capture device, glock number/type, current/target/demote states, holder request state, remote/local demote source, glock flags, DLM reply status/flags, and smoothed timing counters. Log tracepoints capture device, sequence, flush flags, reservation deltas, free log blocks, pin/unpin block number and length, and AIL writeback mode/count. Allocation tracepoints capture inode number, physical block/range length, block state, rgrp address, clone-free blocks, requested reservations, and reserved blocks.

## Dependencies

The header depends on Linux tracepoint infrastructure, buffer heads, DLM constants, writeback controls, iomap, GFS2 in-core state, glocks, and rgrp definitions. It ends with `TRACE_INCLUDE_PATH .`, `TRACE_INCLUDE_FILE trace_gfs2`, and `trace/define_trace.h` outside the include guard as required by tracepoint headers.

## Risks And Invariants

Trace events read live glock/rgrp/inode fields without adding primary synchronization; they are for diagnostics and assume callers pass stable objects at trace call sites. Field formats are part of observability tooling, so changes affect scripts. The `gfs2_rs` event uses `container_of(rs, struct gfs2_inode, i_res)`, so only inode-embedded reservations are valid.

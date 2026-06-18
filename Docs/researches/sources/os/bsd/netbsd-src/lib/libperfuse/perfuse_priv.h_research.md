# File Research: sources/os/bsd/netbsd-src/lib/libperfuse/perfuse_priv.h

## Purpose
Private `libperfuse` state, node metadata, queue types, macros, and operation prototypes.

## Main Responsibilities
- Defines `struct perfuse_state`, including mount metadata, counters, feature flags, callback table, trace queue, nodeid hash table, and PUFFS root.
- Defines `struct perfuse_node_data`, including read/write FUSE file handles, FUSE nodeid, parent nodeid, lookup counters, lock owner, readdir buffers, queued continuations, flags, cached name, and in-flight counters.
- Defines per-node queue types for readdir, read/write, open, resize, ref, and post-exchange waits.
- Provides payload/header accessor macros around callback methods.
- Declares all private helpers and operation entry points implemented in `ops.c` and `subr.c`.

## Key Flags
- State: `PS_NO_ACCESS`, `PS_NO_CREAT`, `PS_INLOOP`, `PS_NO_FALLOCATE`.
- Node: `PND_RECLAIMED`, `PND_INREADDIR`, `PND_DIRTY`, `PND_RFH`, `PND_WFH`, `PND_REMOVED`, `PND_INWRITE`, `PND_INOPEN`, `PND_INVALID`, `PND_INRESIZE`.

## Dependencies
- `perfuse_if.h`, private FUSE protocol definitions, PUFFS.

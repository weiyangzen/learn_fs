# File Research: sources/os/linux/linux/mm/shrinker_debug.c

Provides debugfs visibility and manual scan control for registered shrinkers. It creates `/sys/kernel/debug/shrinker/<name-id>/count` and `scan` files for each shrinker once debugfs is available.

Key responsibilities:
- Maintains a shrinker debugfs root and an IDA for unique per-shrinker debugfs ids.
- Counts shrinker objects per node and per memcg through the shrinker's `count_objects()` callback.
- Implements a `count` seq_file that prints one line per memcg with nonzero objects: memcg id followed by per-node counts.
- Implements a write-only `scan` file accepting `memcg_id nid nr_to_scan` to invoke `scan_objects()` manually.
- Adds debugfs directories/files when shrinkers register and creates entries for already-registered boot shrinkers at late init.
- Supports runtime debugfs renaming and detach/remove during shrinker free.

Important behavior:
- Non-NUMA-aware shrinkers are counted only on node 0; other nodes report zero.
- Non-memcg-aware shrinkers only accept memcg id 0 in the manual scan interface.
- Manual scans validate node id, memcg existence, and memcg online state before calling the shrinker.
- `shrinker_debugfs_add()` expects `shrinker_mutex` to be held and gracefully does nothing before the debugfs root exists.
- Removal is split into detach under `shrinker_mutex` and recursive debugfs removal outside the mutex.

Dependencies:
- Uses debugfs, seq_file, IDA allocation, user copy, memcg iteration/id lookup, shrinker callbacks, and the global shrinker list/mutex exported from the shrinker core.

Notable risks:
- Debugfs callbacks call shrinker methods directly with `GFP_KERNEL`; these files are diagnostic/control surfaces and can induce reclaim behavior if written by privileged users.
- Count output can be expensive on systems with many memcgs and NUMA nodes because it iterates memcgs and calls every shrinker's count callback.
- Lifetime safety depends on the core shrinker registration/free path detaching debugfs before final RCU free.

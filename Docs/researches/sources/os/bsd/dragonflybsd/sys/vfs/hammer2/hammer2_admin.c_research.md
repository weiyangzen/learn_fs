# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_admin.c

HAMMER2 helper-thread and XOP administration implementation, including worker thread signaling, lifecycle management, XOP allocation, dispatch, collection, retirement, and the primary XOP worker loop.

Key responsibilities:
- Defines storage XOP descriptors for HAMMER2 frontend/backend operations, including inode cluster, readdir, resolve, unlink, rename, scans, lookup, delete, inode create/destroy/connect/flush/sync, strategy read/write, and bmap.
- Implements atomic helper-thread signaling, signal-with-clear, wait-for-flags, wait-for-any-with-timeout, and wait-for-clear operations.
- Creates, freezes, unfreezes, remasters, and deletes HAMMER2 helper threads.
- Allocates and initializes XOP requests from `cache_xops`, including modify transaction IDs and inode references.
- Attaches operation names and up to three additional inode references to XOPs.
- Creates and cleans up per-PFS XOP worker groups.
- Starts XOPs across cluster elements, selecting worker groups differently for strategy I/O and non-strategy operations.
- Retires XOPs from frontend and backend participants, caches returned chains in the inode ccache, drains FIFOs, drops inode/name references, and returns XOPs to the object cache.
- Feeds backend chain results through per-cluster FIFOs to the frontend collector.
- Collects frontend responses, advances cluster elements by key, applies cluster/quorum validation, waits for incomplete results, and reports normal end-of-scan or errors.
- Runs the primary XOP worker thread loop, handling stop/freeze/unfreeze/remaster states and executing queued XOP storage functions.

Important implementation details:
- Thread flags are manipulated with compare-and-set loops and `HAMMER2_THREAD_WAITING` interlocks around `tsleep`.
- XOP worker creation allocates `hammer2_xop_nthreads` groups, each with threads for every chain in the mounted PFS root cluster.
- Strategy XOPs are routed to a worker partition separate from normal XOPs to prevent buffer-cache strategy work from deadlocking behind metadata operations.
- Non-strategy XOPs are routed by inode hash, or spread over CPU-local groups depending on cluster size and `hammer2_spread_workers`.
- `hammer2_xop_next()` uses a small per-thread dependency hash of up to four inodes per XOP to avoid running dependent XOPs concurrently on the same cluster index.
- Backend feed uses bounded per-node FIFOs and stalls when full until the frontend drains entries or detaches.
- Frontend collect skips keys that cannot satisfy quorum and advances `collect_key`, returning `HAMMER2_ERROR_ENOENT` for normal scan exhaustion.
- The worker loop can drop stale queued XOPs if the frontend is no longer active.

Dependencies:
- Includes `hammer2.h`, using HAMMER2 thread, PFS, inode, chain, XOP, cluster, FIFO, object-cache, transaction, and spinlock definitions.
- Calls storage XOP functions declared in `hammer2.h` and implemented primarily in `hammer2_xops.c` and strategy/inode/flush modules.
- Uses DragonFly kernel primitives including `lwkt_create`, `tsleep`, `wakeup`, atomics, CPU fences, TAILQ operations, object caches, and per-CPU identifiers.

Notable risks:
- Comments explicitly warn that thread structures and XOPs can disappear immediately after successful atomic state transitions; post-signal dereferences must remain tightly controlled.
- XOP retirement is shared by frontend and backend paths and can free the object; any caller assumptions after queueing or retire are dangerous.
- Worker selection and dependency hashing are correctness-sensitive for modifying clustered operations; the file notes rename as a problematic multi-inode case.
- FIFO flow control relies on atomic run-mask flags and wakeups; missed wakeups or incorrect mask accounting can stall frontend/backend communication.
- `hammer2_xop_helper_cleanup()` iterates `pfs_nmasters`, while creation uses `iroot->cluster.nchains`; correctness depends on those bounds matching active worker slots.
- Timeout waits map `ETIMEDOUT` to HAMMER2 internal timeout errors, but many waits poll for long intervals, so teardown latency depends on signaling discipline.

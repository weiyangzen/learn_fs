# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/fifonode.h

This header defines FIFOFS/pipe vnode-private data, flags, and kernel interfaces.

Locking:
- `fifolock_t` contains the primary FIFO mutex, reference count, open/close sync flag, condition variable, and padding.
- Comments document fields protected by `flk_lock`, including message queues, counts, flags, open/read/write counts, timestamps, sync counters, and lock ref/sync state.
- FIFO allocation list linkage is protected separately by the ftable lock.

Node model:
- `fifonode_t` stores vnode, real shadowed vnode, pipe inode, peer pipe end, message queue head/tail, shared FIFO lock, byte count, wait condition, writer/reader/open/sync/wait counts, timestamps, list linkage, peer credential/pid, sync state, and flags.
- `fifodata_t` bundles one shared `fifolock_t` and two `fifonode_t` objects for pipe pairs.

Flags:
- Include pipe/send-end/open/close/connld/fast-mode states, reader/writer wait flags, signal/poll/high-water/read-write-busy states, open/read/write occurred markers, band polling, stay-fast, and wait-for-mode-change.
- High/low water marks are `16 KiB` and `0`.

Conversions:
- `VTOF` maps vnode to fifonode.
- `FTOV` maps fifonode to vnode.

Kernel interfaces:
- Vnode ops/template, fnode and pipe caches.
- Initialization, stream/open/close/cleanup/remove, id allocation, vnode conversion, pipe creation, fast flush/mode transitions, stream info, and reader/writer wakeups.
- `Fifohiwat` is tunable only under `FIFODEBUG`; otherwise it aliases the constant.

Dependencies and relationships:
- FIFOFS can operate in a fast internal mode or transition to STREAMS mode.
- Supports both named FIFOs shadowing real filesystem nodes and anonymous pipes.

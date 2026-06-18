# File Research: sources/os/plan9/9front/sys/src/9/port/qio.c

Generic block-list and queued I/O implementation used by devices, networking, console, and streams.

Key responsibilities:
- Defines the opaque `Queue` structure with locks, flow-control state, block list, reader/writer rendezvous, kick/bypass callbacks, and close error.
- Provides block-list helpers: free, length, read, concatenate, pullup, trim, pad, copy, adjust, pack, and discard.
- Implements interrupt-level queue producers/consumers: `qget`, `qconsume`, `qpass`, `qpassnolim`, `qproduce`, `qiwrite`.
- Implements process-level queue reads/writes: `qbread`, `qread`, `qbwrite`, `qwrite`.
- Supports message queues, coalescing reads, bypass callbacks, kick callbacks, nonblocking writes, hangup/close/reopen, and queue limit updates.
- Maintains flow control using logical read/write positions based on allocated block sizes, not only data bytes.

Important behavior:
- `Maxatomic` is 64 KiB; `qwrite()` splits larger writes unless the queue is message-oriented.
- Flow-controlled writers remember their queue position and sleep until their own position drains below the limit.
- `qbwrite()` queues data before sleeping so notes do not interrupt already-queued protocol messages.
- `qclose()` drops queued blocks and wakes readers/writers; `qhangup()` marks closed but preserves queued blocks.
- `qread()` returns zero for initial EOF-style closed reads, then errors on repeated closed reads or non-hangup errors.

Notable risks:
- `qfree()` has no reference accounting and is explicitly marked dangerous.
- Queue positions are unsigned counters; correctness relies on normal wraparound behavior and comparisons cast to `int`.

# File Research: sources/os/bsd/dragonflybsd/sys/sys/pipe.h

Kernel pipe buffer and pipe endpoint structure definitions.

Key responsibilities:
- Defines `struct pipebuf`, with cache-aligned read and write substructures, locks, FIFO indices, blocking request markers, access/modify times, buffer size/pointer, VM object, kqueue info, async I/O state, state flags, and timestamp optimization field.
- Defines pipe state flags for async I/O, reader/writer wait, read EOF, write EOF, and closed.
- Defines `struct pipe`, containing two `pipebuf` endpoints, status-change time, list linkage, open count, inode number, and padding.

Important behavior:
- A pipe object encompasses two pipe buffers; bit 0 in `fp->f_data` identifies which side.
- Read and write metadata are cache-aligned separately to reduce contention.
- Pipe buffers are backed by VM objects and integrate with kqueue/select/poll and signal-driven I/O.

Dependencies:
- Kernel/kernel-structures only.
- Includes `types.h`, `time.h`, `event.h`, `xio.h`, `thread.h`, and machine `param.h`.

Notable risks:
- Endpoint selection by pointer low bit requires careful masking and alignment assumptions.
- Reader/writer locks and wait flags must be coordinated to avoid missed wakeups.

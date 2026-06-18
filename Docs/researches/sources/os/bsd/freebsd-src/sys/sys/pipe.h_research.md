# File Research: sources/os/bsd/freebsd-src/sys/sys/pipe.h

This header defines kernel pipe buffer and endpoint structures. It sets default pipe sizes (`PIPE_SIZE`, `BIG_PIPE_SIZE`, `SMALL_PIPE_SIZE`), direct-write threshold (`PIPE_MINDIRECT`), and maximum page slots for direct mappings (`PIPENPAGES`).

`struct pipebuf` tracks circular buffer count, input/output offsets, buffer size, and KVA pointer. `struct pipemapping` supports direct transfers by recording count, position, number of wired pages, and page array. Pipe state bits cover async I/O, reader/writer waiters, rundown, select activity, EOF, pointer/data exclusive access, direct write active, and direct mode eligibility. `PIPE_TYPE_NAMED` marks named pipes.

`struct pipe` is one endpoint in a bidirectional pair. It contains the buffer, direct mapping state, select info, timestamps, async signal info, peer/container pointers, state/type/presence fields, waiter/busy counters, named-pipe writer generation, and fake inode number. `struct pipepair` contains read/write endpoints, mutex, MAC label pointer, and owner credential for accounting. Macros expose pipe mutex locking/assertions.

Kernel prototypes cover destruction, named pipe construction, and select wakeup. Filesystem relevance is direct for FIFO/named-pipe behavior and VFS file operations: pipe endpoints are represented as file objects, expose stat-like metadata, and coordinate readiness with select/poll/kqueue paths.

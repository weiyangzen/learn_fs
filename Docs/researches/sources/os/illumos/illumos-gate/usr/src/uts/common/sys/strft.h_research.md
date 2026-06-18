# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/strft.h

`strft.h` defines the private STREAMS flow-trace subsystem used to record how messages move through a stream. It includes `stream.h` and attaches its trace header through `dblk_t` via `DB_FTHDR()`.

The event namespace uses `FTEV_MASK` for event IDs and reserved high bits for write-side/read-side markers, context-switch markers, and processor markers (`FTEV_ISWR`, `FTEV_CS`, `FTEV_PS`). Defined event groups cover message allocation/free/copy/dup events and queue operations such as put, putq, getq, rmvq, insq, flushq, putnext, and rwnext.

Trace storage is a linked list of fixed-size event blocks. `ftevnt_t` records timestamp, module/driver name, next module/driver name, event, event data, and optional stack pointer. `ftstk_t` stores up to `FTSTK_DEPTH` program counters. `ftblk_t` stores `FTBLK_EVNTS` events plus the next index. `fthdr_t` is attached to a data block and holds the tail block, accumulated hash, last thread/CPU, and the first event block.

Kernel-only declarations expose `str_ftevent()`, `str_ftfree()`, and flow-trace switches `str_ftnever` and `str_ftstack`. `STR_FTALLOC()` lazily allocates a trace header from `fthdr_cache`, initializes the first block and ownership metadata, and records an allocation event. `STR_FTEVENT_MSG()` walks an `mblk_t` continuation chain and records an event on each traced block. `STR_FTEVENT_MBLK()` records an event on a single block.

The subsystem is explicitly private and performance-sensitive: all macros check `str_ftnever` before doing work, allocation is non-sleeping, and stack capture is optional.

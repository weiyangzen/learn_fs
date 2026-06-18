# File Research: sources/os/bsd/freebsd-src/sys/kern/tty_outq.c

## Purpose
Implements the TTY output queue, a simpler block queue used for terminal output buffering and driver/PTM reads.

## Main Structures and State
- `struct ttyoutq_block`: singly-linked data block.
- `ttyoutq_zone`: UMA zone for output blocks.
- Queue offsets track begin, end, first/last blocks, block count, and quota.

## Core Behavior
- `ttyoutq_setsize()` sets quota and allocates blocks while temporarily dropping the TTY lock.
- `ttyoutq_free()` flushes and frees all blocks.
- `ttyoutq_flush()` resets begin/end offsets without freeing blocks.
- `ttyoutq_write()` appends bytes up to available quota.
- `ttyoutq_write_nofrag()` requires enough room for an entire write.
- `ttyoutq_read()` copies bytes into a kernel buffer and recycles blocks.
- `ttyoutq_read_uio()` copies output directly to userspace where possible, temporarily removing whole blocks during `uiomove()`.

## Dependencies
Used by the tty line discipline, tty core drain/flush logic, PTY master reads, and driver output wakeup paths.

## Notes and Risks
- Unlike the input queue, there are no quote bits or canonical boundaries.
- Fast-path UIO reads depend on careful block removal/recycling while the TTY lock is dropped.

# File Research: sources/os/bsd/netbsd-src/sys/kern/tty_subr.c

## Purpose

`tty_subr.c` implements the clist queue primitives used by NetBSD tty input/output buffering. The clists are ring buffers with optional per-character quote-bit tracking.

## Main Responsibilities

- Allocates and frees clist backing storage.
- Provides single-character get/put/unput operations.
- Provides bulk queue-to-buffer and buffer-to-queue transfers.
- Flushes bytes from a queue.
- Counts contiguous queue bytes up to flag-matching characters.
- Iterates queue contents for tty echo/retype logic.
- Concatenates queues.

## Core Data Model

A `struct clist` stores a circular byte buffer with start/end pointers, first/last pointers, capacity, count, and optional quote metadata. With `QBITS` enabled, quote state is stored as a compact bit array rather than one byte per character.

## Behavior

`putc()` and `b_to_q()` append data and maintain quote state. `getc()`, `q_to_b()`, `ndflush()`, and `unputc()` consume or remove data while updating ring pointers and counts. `getc()` wipes consumed bytes to avoid information disclosure.

`firstc()` and `nextc()` provide cursor-style traversal for callers that prevent concurrent queue mutation. `catq()` drains one clist into another with `getc()`/`putc()`.

## Concurrency Notes

Most mutating primitives raise to `spltty()` while manipulating ring state. Higher-level tty code generally also uses `tty_lock` around clist operations that interact with terminal state.

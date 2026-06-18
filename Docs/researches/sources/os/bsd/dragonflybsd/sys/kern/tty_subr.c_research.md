# File Research: sources/os/bsd/dragonflybsd/sys/kern/tty_subr.c

## Summary
Implements tty `clist` queue primitives using a circular buffer of `short` entries that preserves `TTY_QUOTE` metadata with each character.

## Main Responsibilities
- Allocates, reallocates, and frees clist backing buffers.
- Provides queue operations: get, put, unput, flush, concatenate, bulk queue-to-buffer, and buffer-to-queue.
- Provides `clist_nextc` iterator for echo/retype logic without consuming queue data.

## Important Behavior
`clist_alloc_cblocks` preserves existing queued data across resize up to the new capacity. `clist_putc` stores only `TTY_QUOTE | TTY_CHARMASK`. `clist_btoq` returns the number of bytes not copied, while `clist_qtob` returns bytes copied.

## Risks
There is no internal locking; callers must hold the tty-specific token or equivalent. `clist_catq` drops data silently if the destination fills because it ignores `clist_putc` failure. Iterator pointers from `clist_nextc` are only logical tokens and must not be dereferenced by callers.

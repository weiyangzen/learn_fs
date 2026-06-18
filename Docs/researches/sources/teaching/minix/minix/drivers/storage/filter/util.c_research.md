# File Research: sources/teaching/minix/minix/drivers/storage/filter/util.c

## Purpose

Provides small utility helpers for the filter driver: conditional contiguous-memory allocation and a single outstanding alarm abstraction.

## Main Entry Points

- `flt_malloc()`: returns a supplied static buffer when large enough; otherwise allocates contiguous memory with `alloc_contig()`.
- `flt_free()`: frees only dynamically allocated buffers, leaving static backing buffers untouched.
- `flt_alarm()`: sets, clears, or queries the filter driver's single alarm deadline.

## Control Flow And State

`flt_malloc()` is optimized for common small transfers by reusing caller-provided static buffers. Larger requests are contiguous allocations and panic on failure. `flt_alarm()` maintains `next_alarm`; negative `dt` queries the current alarm, zero clears an existing one, and positive values set a new alarm using `sys_setalarm()` and `getticks()`.

## Dependencies

Uses MINIX contiguous allocation/free routines, `sys_setalarm()`, `getticks()`, and shared declarations from `inc.h`.

## Risks

The alarm helper intentionally supports only one active alarm and panics on clearing an unset alarm or overwriting an existing one. Callers must pair `flt_malloc()` and `flt_free()` with the same size/static-buffer arguments or risk freeing static memory incorrectly.

# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_stack.c

## Purpose

`subr_stack.c` implements generic kernel stack-trace storage, printing, sbuf formatting, and symbol lookup helpers. It provides the `stack` feature and supports normal live-kernel symbol lookup plus DDB-safe lookup paths.

## Main Data Model

`struct stack` is defined in `sys/stack.h` and contains a bounded array of program counters plus a `depth` count. This file enforces `depth <= STACK_MAX` before printing or formatting.

Allocation uses `M_STACK`.

## Basic Operations

`stack_create(flags)` allocates and zeroes a stack object.

`stack_destroy(st)` frees it.

`stack_put(st, pc)` appends a program counter if there is room, returning `0`; otherwise it returns `-1`.

`stack_copy(src, dst)` copies the full stack object by assignment.

`stack_zero(st)` clears the stack.

## Printing

`stack_print(st)` prints one line per frame with frame index, PC, symbol name, and offset. It uses the normal linker symbol lookup path and `M_WAITOK`.

`stack_print_short(st)` prints frames compactly on one line, using symbol+offset where available and raw PC otherwise.

`stack_print_ddb(st)` uses DDB linker lookup and prints long format.

When `DDB` or `WITNESS` is enabled, `stack_print_short_ddb(st)` provides compact DDB-safe output.

## sbuf Formatting

`stack_sbuf_print_flags(sb, st, flags, format)` formats the stack into an `sbuf`. It supports:

- `STACK_SBUF_FMT_LONG`: one line per frame.
- `STACK_SBUF_FMT_COMPACT`: symbol+offset tokens on one line.

If symbol lookup returns `EWOULDBLOCK`, the function returns that error, allowing callers using `M_NOWAIT` to avoid sleeping. It newline-terminates output through `sbuf_nl_terminate()`.

`stack_sbuf_print(sb, st)` uses long format and `M_WAITOK`.

When `DDB` or `WITNESS` is enabled, `stack_sbuf_print_ddb()` formats using DDB lookup.

## KTR Support

With `KTR` and `DDB`, `stack_ktr(mask, file, line, st, depth)` emits stack frames as KTR tracepoints up to the requested depth, or the full captured depth when `depth` is zero or larger than actual depth.

## Symbol Lookup

`stack_symbol(pc, namebuf, buflen, offset, flags)` uses `linker_search_symbol_name_flags()`. If lookup fails, it returns `"??"` with offset zero and `ENOENT`. It preserves `EWOULDBLOCK` distinctly.

`stack_symbol_ddb(pc, name, offset)` uses DDB linker symbol APIs, avoids normal linker locking, and also falls back to `"??"`.

## Dependencies

The file depends on linker symbol APIs, `sbuf`, optional DDB/WITNESS/KTR, malloc, sysctl feature registration, and machine-specific stack capture code supplied elsewhere.

## Maintenance Notes

This file does not capture stacks itself; it stores and renders stacks captured by architecture-specific or caller-specific code. The split between normal and DDB symbol lookup is important because DDB contexts cannot safely take the same locks as live-kernel lookup.

Any new formatter should preserve `STACK_MAX` bounds checks and should keep `EWOULDBLOCK` visible when using nonblocking symbol lookup.

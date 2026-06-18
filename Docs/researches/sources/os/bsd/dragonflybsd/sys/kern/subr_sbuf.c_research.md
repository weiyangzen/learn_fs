# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_sbuf.c

## Summary
Implements `sbuf`, a bounded/auto-extending string buffer abstraction shared by kernel and userland builds.

## Main Responsibilities
- Creates and deletes sbufs with static, dynamic, or dynamically allocated structure storage.
- Supports append, copy, printf formatting, trim, set position, finish, data, length, and error inspection.
- Supports optional drain callbacks for streaming output.
- Kernel build adds `sbuf_uionew()`, `sbuf_bcopyin()`, and `sbuf_copyin()`.
- Supports nested sections and padding via `sbuf_start_section()` / `sbuf_end_section()`.

## Important Behavior
Auto-extension grows to powers of two up to a page-sized threshold and then rounds by page-sized increments. Finished sbufs are NUL-terminated and must be finished before `sbuf_data()`. Drain callbacks consume buffered bytes and may leave remaining data shifted to the front.

## Risks
Most operations assert correct unfinished/finished state only under invariants. Copyin helpers reject or truncate based on available space and extension success. Drained sbufs cannot use APIs that require stable internal data.

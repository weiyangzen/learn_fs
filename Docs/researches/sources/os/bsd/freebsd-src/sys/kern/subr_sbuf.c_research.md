# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_sbuf.c

## Purpose

`subr_sbuf.c` implements FreeBSD’s `sbuf` string-buffer abstraction for both kernel and userland builds. An `sbuf` is an append-oriented string builder with optional automatic extension, optional drain callbacks, tracked error state, finish semantics, section accounting, and kernel-only copyin/uio helpers.

## Main Data Model

The implementation operates on `struct sbuf` from `sys/sbuf.h`. Important fields used here include:

- `s_buf`: backing character buffer.
- `s_size`: backing buffer size.
- `s_len`: current logical length.
- `s_error`: accumulated error.
- `s_flags`: dynamic/fixed/finished/drain/section/user flags.
- `s_drain_func`, `s_drain_arg`: optional overflow drain.
- `s_rec_off`, `s_sect_len`: record/section bookkeeping.

Important flags include `SBUF_DYNAMIC`, `SBUF_DYNSTRUCT`, `SBUF_FINISHED`, `SBUF_AUTOEXTEND`, `SBUF_INSECTION`, `SBUF_INCLUDENUL`, `SBUF_DRAINATEOL`, and `SBUF_DRAINTOEOR`.

## Allocation And Growth

Kernel builds allocate from `M_SBUF`; userland builds use `calloc/free`. `sbuf_extendsize()` rounds small buffers up by powers of two and large buffers by page-sized increments.

`sbuf_new(s, buf, length, flags)` initializes a caller-provided or heap-allocated `sbuf`. If no backing buffer is supplied, it allocates one and marks it dynamic. `SBUF_AUTOEXTEND` allows small initial sizes because the function rounds up.

`sbuf_extend(s, addlen)` grows the backing store when auto-extension is enabled. It preserves existing content, frees old dynamic storage, and turns static storage into dynamic storage after the first growth.

`sbuf_delete()` frees dynamic buffer storage, clears the object, and frees the object itself if it was dynamically allocated.

## Append And Copy Operations

`sbuf_put_bytes()` and `sbuf_put_byte()` are the central append helpers. They enforce unfinished state, stop early on prior error, drain or extend on overflow, then copy bytes and update section length.

Public append/copy APIs include:

- `sbuf_bcat()`, `sbuf_bcpy()` for raw bytes.
- `sbuf_cat()`, `sbuf_cpy()` for strings.
- `sbuf_putc()` for one character.
- `sbuf_printf()` and `sbuf_vprintf()` for formatted output.
- Kernel-only `sbuf_bcopyin()`, `sbuf_copyin()`, and `sbuf_uionew()`.

Kernel `sbuf_vprintf()` uses `kvprintf()` with a character callback. Userland `sbuf_vprintf()` uses `vsnprintf()`, extending or draining until enough room exists.

## Draining

`sbuf_set_drain()` installs a drain function and context. It asserts that changing the drain on a non-empty buffer is not allowed unless it is the same function.

`sbuf_drain()` calls the drain callback with either the whole buffer or, with drain-to-end-of-record semantics, only up to `s_rec_off`. It handles positive progress, converts zero progress to `EDEADLK`, records negative callback returns as errors, preserves newline-at-end state, and compacts remaining data to the front.

`sbuf_count_drain()` is a drain callback that only counts bytes, useful for sizing sysctl output without materializing it.

## Finish, Data, And Length

`sbuf_finish()` writes a terminating NUL at `s_len`, optionally includes that NUL in logical length, drains remaining data if a drain is installed, and marks the buffer finished. Kernel builds return the stored error; userland builds set `errno` and return `-1` on error.

`sbuf_data()` requires a finished non-draining buffer and returns `s_buf`.

`sbuf_len()` returns `-1` on error and otherwise reports logical length, accounting for `SBUF_INCLUDENUL`.

`sbuf_done()` tests the finished flag.

## Position, Trimming, And Sections

`sbuf_clear()` resets length, record offset, section length, error, and finished flag.

`sbuf_setpos()` truncates to an existing position and rejects section mode.

`sbuf_trim()` removes trailing whitespace, updating section length if needed.

`sbuf_nl_terminate()` appends a newline to non-empty output if the last emitted byte was not already newline, including the drained-buffer case tracked by `SBUF_DRAINATEOL`.

`sbuf_start_section()` begins a section or subsection, storing prior section length for nested sections. `sbuf_end_section()` pads the section to an alignment with a specified character, returns section length, and restores outer-section accounting.

## Invariants

In kernel invariant builds, helper assertions check non-null initialized buffers, bounds, and whether functions are called in finished or unfinished state. Many operations also assert that drains are absent when random access or direct data inspection would be nonsensical.

## Maintenance Notes

The buffer’s error state is sticky: most append APIs return failure once `s_error` is set. Drain behavior is the most subtle part because it allows output to leave the buffer before finish, so functions that inspect `s_buf` must reject drain-enabled buffers.

Section accounting depends on every append path updating `s_sect_len`; future append helpers must preserve that behavior.

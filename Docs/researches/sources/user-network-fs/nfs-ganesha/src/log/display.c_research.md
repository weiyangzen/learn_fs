# sources/user-network-fs/nfs-ganesha/src/log/display.c

## Purpose
This source implements `display_buffer`, a bounded string-building helper used by logging and diagnostics to append formatted text, opaque byte strings, and truncated strings safely.

## Important APIs, Types, And Control Flow
Internal `_display_buffer_remain` computes remaining bytes including the null terminator. `display_buffer_remain` validates/reset buffer pointers and marks too-small buffers as overflowed. `_display_complete_overflow` places `...` while avoiding partial UTF-8 truncation. `display_start` prepares append operations and handles already-full buffers. `display_finish` finalizes after writes and applies overflow ellipsis. `display_force_overflow` deliberately marks truncation. `display_vprintf` wraps `vsnprintf`. `display_opaque_bytes_flags` formats bytes in hex with flags for uppercase, `0x`, and invalid input handling. `display_opaque_value_max_impl` prints printable opaque values or hex with length/truncation markers. `display_len_cat` appends length-delimited strings, and `display_cat_trunc` appends a null-terminated string through a sub-buffer for caller-specified truncation.

## State And Persistence
All state is caller-owned in `struct display_buffer` fields `b_start`, `b_current`, and `b_size`. The implementation mutates the current pointer and buffer contents but does not allocate or persist data.

## Dependencies And Integration Points
It includes C runtime headers and `display.h`. Many SAL, stats, ID, state, and logging formatters use display buffers to build bounded diagnostic strings without heap allocation.

## Risks And Test Signals
Critical risks include pointer validation, small-buffer behavior, UTF-8 boundary handling, negative lengths, null opaque values, `vsnprintf` return semantics, and nested sub-buffer truncation. Tests should cover invalid buffers, sizes 0-4, exact fit, overflow, multibyte UTF-8 truncation, printable/non-printable opaque data, `OPAQUE_BYTES_NO_TRUNC`, and repeated appends after overflow.

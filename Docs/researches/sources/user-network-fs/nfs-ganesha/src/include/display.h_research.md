# sources/user-network-fs/nfs-ganesha/src/include/display.h

## Purpose
`display.h` defines a safe append-only string formatting buffer used throughout Ganesha logging and diagnostics. It provides primitives for printf-style appending, string concatenation, truncation, and rendering opaque data as printable strings or hex.

## Important APIs, Types, And Functions
`struct display_buffer` stores total size, start pointer, and current append pointer. Core APIs are `display_buffer_remain`, `display_start`, `display_finish`, `display_force_overflow`, `display_reset_buffer`, `display_buffer_len`, `display_vprintf`, `display_printf`, `display_opaque_bytes_flags`, `display_opaque_bytes`, `display_opaque_value_max_impl`, `display_opaque_value_max`, `display_opaque_value`, `display_len_cat`, `display_cat`, and `display_cat_trunc`. Opaque rendering flags control hex case, `0x` prefix, invalid argument handling, and truncation policy.

## Control Flow
Display primitives call `display_start`, copy or format bounded bytes, then call `display_finish`. Once a buffer fills, implementation marks overflow and writes an ellipsis while trying not to split a UTF-8 character. Non-primitive display routines may compose other display functions and rely on the last primitive to finish the buffer.

## State And Persistence
The only state is caller-owned buffer memory and the current pointer. There is no global state and no persistence. Overflow is represented by moving `b_current` to the logical end and leaving a valid NUL-terminated truncated string.

## Dependencies And Integration Points
It depends on libc formatting/string headers and is implemented by `log/display.c`. Callers include NFS state owner/session display, NLM utilities, file handle display macros, FSAL attribute logging, export option logging, recovery code, and handle mapping code.

## Risks
Callers must initialize `struct display_buffer` with valid size/start/current values and must not write directly without respecting `display_start`/`display_finish`. Small buffers below four bytes are forced empty/overflowed. Return values matter: callers that ignore `<=0` will not overflow memory, but diagnostic output may be incomplete. Opaque value display scans `len` bytes for printability even when `max` is smaller, so very large inputs can cost more than expected.

## Test Signals
`log/test_display.c` exercises repeated appends, overflow, reset, printf, and opaque rendering with printable and non-printable inputs. Additional tests should cover invalid buffers, tiny buffers, UTF-8 truncation, invalid length/null/empty flags, `OPAQUE_BYTES_NO_TRUNC`, uppercase/lowercase hex, and nested display functions.

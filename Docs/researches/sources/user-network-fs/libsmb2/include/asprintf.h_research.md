# sources/user-network-fs/libsmb2/include/asprintf.h

## Purpose
`asprintf.h` provides inline fallback implementations of `_vscprintf`, `vasprintf`, and `asprintf` for platforms lacking those libc functions.

## Important APIs, Types, and Functions
`_vscprintf_so()` computes formatted length with `vsnprintf(NULL, 0, ...)` using `va_copy`. `vasprintf()` allocates a buffer of computed length plus terminator and formats into it. `asprintf()` wraps `vasprintf()` with varargs. Xbox maps `inline` to `__inline` and uses `_vscprintf`/`_vsnprintf`.

## Control Flow
Callers invoke `asprintf()`, which starts a `va_list`, delegates to `vasprintf()`, then ends the list. `vasprintf()` computes required length, allocates, formats, stores the output pointer, and returns the formatted byte count or `-1`.

## State and Persistence Behavior
The only persistent state is heap memory returned through `*strp`; callers must free it. On format failure after allocation, the function frees the buffer before returning `-1`.

## Dependencies and Integration Points
It depends on `<stdio.h>`, `<stdlib.h>`, `<stdarg.h>`, and usually `<malloc.h>`. It is distributed as a non-installed portability header used internally where `asprintf` is not available.

## Risks and Edge Cases
If `vsnprintf(NULL, 0, ...)` is not supported by a target, length calculation fails. The fallback is guarded with `#ifndef asprintf`/`vasprintf`, which detects macros but not necessarily external functions. Allocation size can overflow if `len` is near `INT_MAX`.

## Test Signals
Compile on MSVC/Xbox/MinGW and POSIX targets, format empty and long strings, force allocation failure where possible, and verify callers free returned buffers.

# File Research: sources/os/bsd/netbsd-src/lib/libexecinfo/unwind.c

## Purpose
Primary `backtrace()` implementation using `_Unwind_Backtrace`.

## Main Components
- `struct tracer_context` stores output array, requested length, and current count.
- `tracer()` skips the `backtrace` frame, records instruction pointers from `_Unwind_GetIP()`, and stops when the output array is full.
- `backtrace()` initializes context, invokes `_Unwind_Backtrace()`, skips the final frame below `__start`, and returns captured frame count.

## Integration
Built when `USE_UNWIND=yes`, which is the default in the Makefile.

## Risks / Notes
Depends on platform unwind support. Captured instruction pointers are later symbolized by `backtrace.c`.

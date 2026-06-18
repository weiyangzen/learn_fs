# File Research: sources/os/bsd/netbsd-src/lib/libexecinfo/builtin.c

## Purpose
Fallback implementation of `backtrace()` using compiler frame-address support instead of libunwind.

## Main Components
- Defines stack comparison direction using `__MACHINE_STACK_GROWS_UP`.
- Defines `struct frameinfo` with next-frame pointer and return address.
- `backtrace()` starts from `__builtin_frame_address(0)`, walks frame links, stores return addresses, and stops when the frame crosses the current stack boundary or `len` is reached.

## Integration
Used when `USE_UNWIND` is not enabled in the Makefile.

## Risks / Notes
This approach depends on frame pointers and ABI frame layout, so optimized builds or architectures without reliable frame chains may produce incomplete or invalid traces.

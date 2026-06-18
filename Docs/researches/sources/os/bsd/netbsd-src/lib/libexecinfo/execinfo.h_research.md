# File Research: sources/os/bsd/netbsd-src/lib/libexecinfo/execinfo.h

## Purpose
Public header for NetBSD `libexecinfo`.

## Main Content
- Provides `size_t` via NetBSD feature-test headers when needed.
- Declares C-linkage APIs:
  - `backtrace_sandbox_init`
  - `backtrace_sandbox_fini`
  - `backtrace`
  - `backtrace_symbols`
  - `backtrace_symbols_fd`
  - `backtrace_symbols_fmt`
  - `backtrace_symbols_fd_fmt`

## Integration
Installed as `/usr/include/execinfo.h` and consumed by applications requiring glibc-like backtrace APIs plus NetBSD format variants.

## Risks / Notes
The public API returns heap-allocated symbol arrays for the `backtrace_symbols*` functions that return `char **`; callers must free them.

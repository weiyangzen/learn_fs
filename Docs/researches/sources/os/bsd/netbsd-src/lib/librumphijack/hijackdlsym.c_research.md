# File Research: sources/os/bsd/netbsd-src/lib/librumphijack/hijackdlsym.c

Read completely: 60 lines.

## Purpose
Provides an out-of-line `dlsym()` wrapper for `librumphijack` and `librumpclient` preload scenarios.

## Main Responsibilities
- Includes `rumpuser_port.h`, `<dlfcn.h>`, and `hijack.h`.
- Implements a `__noinline` `bouncer()` that calls `dlsym(handle, symbol)`.
- Implements `rumphijack_dlsym()` as a call through `bouncer()`.

## Key Implementation Notes
- The source comments say this is called from `librumpclient` when using `LD_PRELOAD` to ensure the correct `RTLD_NEXT` behavior.
- The file is intentionally compiled with `-O0` so the wrapper is not optimized into a tail call or otherwise transformed in a way that changes dynamic-linker stack semantics.
- A comment notes the extra indirection is required for PowerPC.

## Filesystem Relevance
Indirect. It makes the syscall-interposition layer robust enough to find host symbols while routing filesystem and socket calls through `hijack.c`.

## Dependencies
- `dlsym(3)` from the dynamic linker.
- Local declaration in `hijack.h`.

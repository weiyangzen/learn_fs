# File Research: sources/os/bsd/netbsd-src/lib/libc/compat-43/getwd.c

## Scope

Compatibility implementation of unsafe historical `getwd()`.

## Behavior

- Emits a link-time warning recommending `getcwd()`.
- Calls `getcwd(buf, MAXPATHLEN)`.
- On failure, copies `strerror(errno)` into `buf` and returns `NULL`.

## Dependencies And Invariants

- Requires caller-provided `MAXPATHLEN` buffer.
- Preserves historical behavior of placing the error string in the supplied buffer.

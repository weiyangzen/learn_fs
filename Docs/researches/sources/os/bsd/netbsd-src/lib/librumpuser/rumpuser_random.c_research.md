# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_random.c

## Purpose
Provides rumpuser random-byte acquisition for rump kernel consumers.

## Main Interfaces
Exports `rumpuser__random_init()` and `rumpuser_getrandom()`.

## Control Flow And State
When `HAVE_ARC4RANDOM_BUF` is available, initialization is a no-op and `rumpuser_getrandom` fills the buffer with `arc4random_buf`. Otherwise initialization opens `/dev/urandom` read-only into a static file descriptor and `rumpuser_getrandom` reads from it.

Each call caps output to `random_maxread`, currently 32 bytes, and returns the number of bytes actually provided through `retp`. The `flags` argument is accepted but ignored.

## Dependencies
Uses `arc4random_buf` when available, or host `open`/`read` on `/dev/urandom`. Uses rumpuser error-return conventions through `ET`.

## Risks And Notes
The non-arc4random path requires successful initialization before use and keeps a process-global descriptor. Short reads are reported via `retp` without an internal retry loop. The fixed 32-byte cap means callers must loop for larger requests.

# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/send/skipequiv.c

Read fully: 92 lines, 1747 bytes. SHA-256 prefix: `9c33ed67d265c31d`.

This file implements system-equivalence lookup used to strip already-local or equivalent systems from bang paths. `skipequiv()` walks leading `system!` components and skips each component found in the `equivlist`.

`lookup()` opens and caches local/global upas library files, then delegates membership tests to `okfile()`. `okfile()` scans comma/whitespace-separated tokens and requires exact token boundaries.

Integration: exported through `send.h`; used by send routing/rewrite paths to avoid forwarding loops through equivalent system names. It depends on `abspath()`, `UPASLIB`, `sysopen()`, and Plan 9 `Biobuf` line APIs.

Risk notes: `skipequiv()` temporarily writes NUL bytes into the supplied address string while parsing. Callers must pass mutable storage, not string literals or shared immutable buffers.

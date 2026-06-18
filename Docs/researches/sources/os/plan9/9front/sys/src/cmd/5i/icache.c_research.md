# File Research: sources/os/plan9/9front/sys/src/cmd/5i/icache.c

This file contains empty instruction-cache hooks for `5i`.

Functions:
- `icacheinit()` does nothing.
- `updateicache(ulong addr)` ignores the address.

Dependencies and interactions:
- `mem.c:ifetch()` calls `updateicache()` when `icache.on` is enabled.
- `arm.h` declares `initicache()`, but this file defines `icacheinit()`; naming mismatch may be intentional legacy or unused.

Research relevance:
- Simulated I-cache support is effectively disabled/stubbed.

Risk notes:
- I-cache statistics or stall modeling will not work unless implemented elsewhere.
- The `initicache`/`icacheinit` name mismatch is suspicious.

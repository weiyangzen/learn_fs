# File Research: sources/os/plan9/plan9/sys/src/9/pc/init9.c

- Size/hash: 7 lines, 94 bytes, SHA-256 `103787d67b9a00d968d57f7ffe966d83f91281e4373c80f765269b83f0577a10`.
- Purpose: Tiny C entry shim for the first user-space boot program path.
- Contents: Declares `extern void startboot(char*, char**);` and defines `_main(char *argv0)` to call `startboot(argv0, &argv0)`.
- Integration: Bridges architecture-specific startup calling convention to the portable boot startup helper.
- Dependencies: Requires `startboot` from the boot/runtime side.
- Research notes: No filesystem implementation logic, but it participates in initial boot handoff toward `/boot`.

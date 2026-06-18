# File Research: sources/os/plan9/9front/sys/src/cmd/ktrace.c

`ktrace` reconstructs and prints kernel stack traces from a kernel image plus `pc`, `sp`, and optional link register. It can run interactively or consume address=value stack words from stdin.

Key behavior:
- Detects executable architecture with `<mach.h>` and selects `i386trace`, `amd64trace`, generic CISC `ctrace`, or generic RISC `rtrace`.
- Uses symbol table lookups, `.frame` local symbols, `pc2sp()`, and architecture address size to step stack frames.
- Handles special interrupt-return frames for `forkret` on i386 and `noteret` on amd64.
- `printaddr()` emits output as `src(address)` commands with comments suitable for Plan 9 debugging workflows.
- `readstack()` builds a fixed table of up to 1024 address/value pairs; `getval()` looks them up or prompts interactively.

The code is diagnostic tooling and caps traces at about 40 frames to avoid runaway walks.

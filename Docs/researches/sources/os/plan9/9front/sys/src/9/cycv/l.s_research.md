# File Research: sources/os/plan9/9front/sys/src/9/cycv/l.s

Cyclone V ARM bootstrap and low-level assembly support.

Key responsibilities:
- Disables watchdog/L2/MMU early, clears low memory and BSS, builds initial section mappings, enables MMU, and enters `main`.
- Sets vector base and per-mode stacks.
- Provides user return, fork return, and stack setup helpers.
- Implements serial hex debug output.
- Provides interrupt priority functions, atomics, barriers, idle/event, TTBR/TLB/ASID helpers, fault address/status reads, performance counters, and VFP save/restore.
- Implements cache maintenance by range and line.
- Provides physical-address lookup helper `palookur()`.

Important behavior:
- Emits early boot characters through UART for progress.
- Maps KZERO to physical 0 and peripheral region as device/no-exec.
- Stores `Mach*` in `TPIDRPRW`.

Dependencies:
- `mem.h`, `io.h`, trap vector code, MMU setup, and ARMv7 CP15/VFP instructions.

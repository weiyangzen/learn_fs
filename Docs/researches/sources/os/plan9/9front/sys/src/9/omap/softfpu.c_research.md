# File Research: sources/os/plan9/9front/sys/src/9/omap/softfpu.c

Process-level soft-FPU integration hooks.

Key behavior:
- Provides placeholder/proc hooks for FPU save/restore/fork/setup/notify/noted behavior.
- `notefpsave` returns the process FP save area.
- `fpuinit` is effectively empty.
- `fpuemu` calls `fpiarm` to emulate faulting floating-point instructions.
- `fpudevprocio` currently returns 0, so `/proc` FP I/O is not implemented here.

Research notes:
- The real instruction emulation lives in `fpiarm.c`; this file connects it to process and trap plumbing.

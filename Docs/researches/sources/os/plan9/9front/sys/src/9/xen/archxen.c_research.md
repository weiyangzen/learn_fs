# File Research: sources/os/plan9/9front/sys/src/9/xen/archxen.c

Xen PC architecture adapter.

Purpose:
- Registers `PCArch archxen` with Xen-specific reset, interrupt, clock, and timer hooks.

Key behavior:
- `identify` disables PGE capability tracking.
- `intrinit` inspects xenstore CPU availability and honors `*nomp`/`*ncpu`, but ultimately limits the guest to one CPU with an SMP-not-supported message.
- `shutdown` calls `HYPERVISOR_shutdown(1)`.
- Provides placeholder I/O port, CR4, and MTRR functions needed by shared x86 code.

Integration:
- Referenced during Xen `main()` architecture initialization.
- Bridges generic Plan 9 PC kernel paths to Xen hypervisor routines.

Risks/notes:
- SMP discovery exists but SMP startup is explicitly not supported.
- Hardware I/O functions are stubs, suitable only for paravirtualized Xen assumptions.

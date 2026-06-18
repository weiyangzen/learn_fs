# File Research: sources/os/plan9/9front/sys/src/9/mt7688/arch.c

MT7688 MIPS architecture glue for port-layer expectations. It implements idle, address alignment checks, process setup/fork/save/restore stubs, user PC/debug PC helpers, protected register writes for `/proc`, kernel `Ureg` construction for sleeping processes, and kproc child scheduling setup.

`procsetup` initializes floating-point state and copies initial FP status into the process save area. `setregisters` preserves status and `r27` while allowing register updates from devproc.

Notable risks: process save/restore/fork are mostly stubs; comments note some routines may need architecture-specific completion.

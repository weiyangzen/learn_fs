# File Research: sources/os/bsd/freebsd-src/sys/sys/kernel.h

Core kernel initialization and tunable infrastructure header. It declares global clock/kernel variables under `_KERNEL`, then defines the ordered `sysinit_sub_id` initialization phases from tunables and VM through drivers, VFS, networking, syscalls, kthreads, SMP, RACCT, and final init.

`struct sysinit` and the `SYSINIT`/`C_SYSINIT`/`SYSUNINIT` macros place init/uninit records in linker sets, optionally wrapping through TSLOG. Ordering is controlled by subsystem id plus `SI_ORDER_*`.

Kernel tunable macros register typed loader/kernel environment tunables for int, long, ulong, int64, uint64, quad, bool, and string, with matching fetch helpers. The file also defines interrupt configuration hooks (`struct intr_config_hook`) and APIs to establish, disestablish, drain, or schedule one-shot hooks after interrupts are enabled.

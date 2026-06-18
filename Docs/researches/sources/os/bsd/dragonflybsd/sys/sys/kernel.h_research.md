# File Research: sources/os/bsd/dragonflybsd/sys/sys/kernel.h

Kernel-only header for global kernel variables, boot/sysinit ordering, tunables, pseudo-device module registration, and interrupt configuration hooks. It declares host/time/tick globals and the `vmm_guest_type` enum.

The `sysinit_sub_id` enum defines boot ordering, including allocator, KLD, VFS, root configuration, dump configuration, mount-root, and kernel-thread phases. `SYSINIT` / `SYSUNINIT` register ordered init/uninit entries via linker sets. `TUNABLE_INT/LONG/ULONG/QUAD/STR` bind loader/kernel environment tunables into sysinit. Filesystem relevance is high because VFS modules use this ordering and `VFS_SET` ultimately relies on module/sysinit machinery.

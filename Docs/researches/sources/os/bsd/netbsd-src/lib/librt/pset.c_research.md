# File Research: sources/os/bsd/netbsd-src/lib/librt/pset.c

Read completely: 48 lines.

Provides the public `pset_bind()` wrapper for processor sets. It calls the lower-level `_pset_bind()` syscall stub with `P_ALL_LWPS` set to `0`, meaning the operation applies to all LWPs in the selected process/thread scope.

All other processor-set entry points listed in the Makefile are generated syscall stubs.

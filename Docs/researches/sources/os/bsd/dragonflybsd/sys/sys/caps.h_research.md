# File Research: sources/os/bsd/dragonflybsd/sys/sys/caps.h

DragonFly system capability restriction header, defining negative process capability bits and user/kernel APIs for applying or checking restrictions.

Key responsibilities:
- Represents 256 capabilities in `__syscaps_t`, with two bits per capability for SELF/EXEC inheritance state.
- Defines restriction application flags: none, self, exec, all, plus extra flags such as in-parent, nullcred, root-test bypass, and wheel bypass.
- Organizes capabilities into 16 groups, including root restrictions, process/sysctl/time/scheduler controls, exec SUID/SGID, credential mutation, jail, network, VFS, and mount restrictions.
- Declares userland `syscap_get()` and `syscap_set()`.
- Declares kernel helpers for exec inheritance, mutation under lock, and privilege checks against credentials or threads.
- Provides `__SYSCAP_ALLSTRINGS` for name tables.

Dependencies:
- Uses `machine/stdint.h`; kernel prototypes depend on `proc`, `thread`, and `ucred`.

Notable risks:
- Capability names are restrictions, not grants, so policy code must treat set bits as denial state.
- Comments state restrictions cannot be downgraded after application, implying OR-only monotonic semantics.
- The string tables need careful synchronization with numeric constants; group 8/9 string ordering appears suspicious relative to defined VFS capability numbers, and `"novfs_ioct"` appears misspelled.

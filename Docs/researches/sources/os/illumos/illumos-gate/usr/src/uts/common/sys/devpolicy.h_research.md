# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/devpolicy.h

This header defines device policy data structures and kernel APIs for privilege-gated device access. It includes types, privilege sets, param, and vnode.

`devplcysys_t` is the system-call interface structure, carrying major number, minor name, wildcard flags, and variable privilege set data. Macros compute its size and read/write privilege-set pointer locations.

`devplcy_t` is the kernel policy object with reference count, generation, flags, read and write privilege sets, and optional minor name. The file declares `nullpolicy`, global generation counter, refcount helpers, lookup by vnode, initialization, load/get/get-by-name syscalls, and privilege lookup by name.

Token names identify read and write privilege-set fields. Limits include `MAXDEVPOLICY` and default-major marker `DEVPOLICY_DFLT_MAJ`.

Research notes:
- Device policy ties device special files to privilege requirements.
- The system-call payload is variable-sized due to embedded privilege sets.
- Generation count supports cache invalidation or policy freshness checks.

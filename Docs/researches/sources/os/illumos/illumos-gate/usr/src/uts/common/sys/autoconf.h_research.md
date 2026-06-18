# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/autoconf.h

This is a kernel autoconfiguration/DDI support header. It defines driver-name bookkeeping state, driver flags, debug flags/macros, device tree audit/cache structures, and kernel-private autoconfiguration entry points.

Key contents:
- `struct devnames`: per-driver state parallel to the devops list, including name, flags, parent list, lock, instance list, global properties, minor permissions, and instance boundaries.
- `DN_*` flags for parsed config, busy/held/inactive/removed state, network/leaf/nexus-like classifications, no-autodetach, GLDv3, PHCI, SCSI sizing, etc.
- Kernel-only DDI debug flag masks and conditional debug macros.
- `devinfo_audit_t`, `devinfo_log_header_t`, and `struct di_cache`.
- Special devinfo path/cache constants such as `PSEUDO_PATH`, `CLONE_PATH`, `DI_CACHE_FILE`.
- Global kernel symbols and prototypes for driver/device tree setup, mbind handling, reconfiguration state, devinfo cache, forced attach, I/O retire, quiesce checks.

Dependencies:
- Includes DDI/devops/mutex/thread/OBP/hwconf/system headers.
- Most declarations are under `_KERNEL`.

Research notes:
- This is kernel-internal infrastructure, not a user ABI.
- Locking expectations are documented for `dn_lock` and devops reference count macros.
- Several interfaces are marked obsolete or compatibility-only.

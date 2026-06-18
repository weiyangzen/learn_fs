# sources/user-network-fs/nfs-utils/utils/mount/mount_constants.h

Purpose: supplies mount flag definitions not guaranteed by older system headers and defines NFS helper-specific pseudo flags.

Important APIs/data: fallback definitions include `MS_DIRSYNC`, `MS_ACTION_MASK`, `MS_NOATIME`, `MS_NODIRATIME`, `MS_BIND`, `MS_MOVE`, `MS_REC`, `MS_VERBOSE`, `MS_RELATIME`, and `MS_MGC_VAL/MS_MGC_MSK`. It defines `MS_DUMMY`, `MS_USERS`, `MS_USER`, and `MS_NOMTAB`.

Control flow and integration: `mount.c` option parsing sets these flags, and mount/umount code masks helper-only `MS_USER/MS_USERS` before calling `mount(2)`.

State and persistence: no state; constants affect generated mtab options and syscall flags.

Dependencies: included by legacy mount, umount, and NFS protocol code to normalize build environments.

Risks and tests: incorrect flag values can cause wrong kernel behavior or mtab output. Test signals include builds on older headers, generic option parsing, masking pseudo flags before syscall, and remount/no-mtab option handling.

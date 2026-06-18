# sources/security-integrity/selinux/restorecond/restore.h
# sources/security-integrity/selinux/restorecond/restore.h

Purpose: declares restorecon option state and `restore_init()`.

Important APIs and types: `struct restore_opts` holds individual restorecon flags, combined `restorecon_flags`, root path, program name, selabel handle, selabel options, debug flag, and output file. `restore_init()` is declared for initialization.

State and persistence: the struct is the shared mutable state passed to libselinux restorecon operations.

Dependencies and integration points: includes libselinux, label, restorecon, stdio, syslog, stat, and errno headers. Used by restorecond sources.

Risks and test signals: flags are unsigned integers expected to match libselinux constants; misuse can silently alter relabel behavior. No direct tests target this header.

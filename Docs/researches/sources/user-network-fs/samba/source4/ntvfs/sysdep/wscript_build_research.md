# sources/user-network-fs/samba/source4/ntvfs/sysdep/wscript_build

Purpose: This Waf script builds the system-dependent notify and lease abstraction layers and their Linux-specific modules.

Important APIs, types, and functions: It declares `sys_notify_inotify`, `sys_notify`, `sys_lease_linux`, and `sys_lease` using `bld.SAMBA_MODULE` and `bld.SAMBA_SUBSYSTEM`.

Control flow: The inotify module is enabled only when `HAVE_LINUX_INOTIFY` is configured. The Linux lease module is enabled only when `HAVE_F_SETLEASE_DECL` is configured. Generic subsystems always list their C files and dependencies.

State and persistence behavior: The build file has no runtime state. It controls which runtime backends can register with `sys_notify_init` and `sys_lease_init`.

Dependencies and integration points: It links notify code with `events`, `inotify`, `talloc`, and `tevent`; lease code with `tevent` and `talloc`. It is recursed from `source4/ntvfs/wscript_build` when the NTVFS file server is enabled.

Risks: Platform detection controls feature availability, so runtime behavior varies by host. Misconfigured feature tests can expose backend names without working OS support or omit useful modules.

Test signals: Build tests should cover Linux with inotify/F_SETLEASE, non-Linux without them, and module registration lists in generated static module tables.

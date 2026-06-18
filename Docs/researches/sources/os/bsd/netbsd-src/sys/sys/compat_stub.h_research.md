# File Research: sources/os/bsd/netbsd-src/sys/sys/compat_stub.h

Central registry of module hooks and legacy vectors used to decouple optional compatibility modules from core kernel code.

Key content:
- Includes `module_hook.h`, `param.h`, socket and signal type headers.
- Legacy direct vectors for NTP and SCTP compatibility callbacks.
- `MODULE_HOOK` declarations for old USB structs, ccd, clockctl, sppp, cryptodev, RAIDframe, puffs, wscons, sysmon, vnd, ieee80211, if/tty/socket/routing compatibility, old modstat, netbsd32, SunOS emulation, random ioctl, sysvipc, coredump formats, amd64 old syscall handling, and removed IPv6 neighbor-discovery compatibility.
- Exposes `kern_sig_43_pgid_mask`.

Important behavior:
- Header warns that changes require kernel version updates in `sys/param.h` so kernel/modules remain synchronized.
- Mostly forward-declares structs to avoid broad includes.
- Critical for loadable compatibility code paths and ABI preservation across NetBSD releases.

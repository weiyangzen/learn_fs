# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_mib.c

Read completely: 785 lines.

## Purpose
Defines core FreeBSD sysctl MIB roots and many fundamental kernel, hardware, user, compatibility, feature, host identity, jail-visible, and ABI-reporting sysctls.

## Main Elements
- Creates root nodes: `sysctl`, `kern`, `vm`, `vfs`, `net`, `debug`, `hw`, `machdep`, `user`, `p1003_1b`, `compat`, `security`, and optional `regression`.
- Exposes kernel identity, version, compiler version, OS type, process limits, `ARG_MAX`, POSIX feature constants, group limits, boot file, and `maxphys`.
- `sysctl_kern_arnd()` returns random bytes and explicitly zeroes its temporary buffer.
- Hardware sysctls report CPU count, byte order, page size, physical memory, firmware memory, user memory, available pages, and supported page sizes.
- ABI helpers report `hw.machine_arch` adaptively based on the calling process and `kern.supported_archs`.
- `sysctl_hostname()` handles jail-aware hostname, NIS domain, and host UUID reads/writes.
- `sysctl_kern_securelvl()` enforces monotonic securelevel increases across jail descendants, except in regression mode.
- `sysctl_hostid()`, `sysctl_bootid()`, `sysctl_osrelease()`, and `sysctl_osreldate()` expose jail-scoped host ID, random boot ID, OS release, and OS release date.
- `sysctl_build_id()` extracts and formats the ELF build-id note.
- Defines `kern.features.*` compatibility feature flags.
- Defines POSIX/user limit placeholder sysctls and `user.localbase`.
- Adds `debug.sizeof.*` entries for kernel structs including vnode, proc, bio, buf, kinfo_proc, and pcb.
- `sysctl_kern_pid_max()` validates and updates `pid_max` under process-list locks.
- Provides compatibility `kern.fallback_elf_brand`.

## Dependencies And Integration
Integrates with sysctl, jails/prisons, random subsystem, SMP globals, VM memory counters, process locks, ABI/sysent hooks, ELF build metadata, and compatibility options. The `vfs` root created here is the top-level sysctl namespace used by filesystem code.

## Risk Notes
Several sysctls are jail-aware and must preserve prison inheritance rules. Securelevel lowering is intentionally rejected outside regression builds. `boot_id` is unavailable until random seeding succeeds. ABI-adaptive `machine_arch` can change reported values depending on the caller's binary ABI.

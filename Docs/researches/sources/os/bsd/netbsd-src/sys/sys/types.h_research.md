# File Research: sources/os/bsd/netbsd-src/sys/sys/types.h

Read completely: 380 lines.

Defines NetBSD core scalar types, compatibility typedefs, device-number helpers, and common kernel forward declarations.

Key elements:
- Includes machine type and integer definitions, then defines fixed-width integer aliases and BSD `u_int*_t` aliases.
- NetBSD source mode exposes traditional BSD/SysV aliases such as `u_char`, `u_short`, `u_int`, `u_long`, `unchar`, `ushort`, `uint`, and `ulong`.
- Defines filesystem, device, identity, IPC, process, resource, scheduler, CPU, lock, and size/time-related typedefs.
- Kernel/standalone builds define deprecated `boolean_t`, `TRUE`, and `FALSE`.
- NetBSD source mode includes endian compatibility and declares legacy off_t syscall prototypes.
- Defines `major`, `minor`, and `makedev` packing for `dev_t`.
- Defines `kauth_cred_t`, `pri_t`, common kernel forward declarations, and `SET`/`ISSET`/`CLR` macros.
- Userland includes pthread types when feature-test macros require them.

Risks and notes:
- Foundational ABI header; typedef size changes have system-wide impact.
- Device major/minor packing is externally observable.
- Namespace exposure is heavily gated by feature-test macros.

# File Research: sources/os/bsd/dragonflybsd/sys/sys/param.h

Central machine-independent DragonFlyBSD system parameter header.

Key responsibilities:
- Defines historical BSD version macros and `__DragonFly_version` with an extensive version-change log, currently `600519`.
- Includes core type, limit, machine alignment, and machine parameter headers.
- Defines common limits: command name, interpreter, login name, process/file/group limits, hostname, device-name, block/path/symlink sizes, and allocation constants.
- Defines sleep/wakeup flags and wakeup domain/cpu encoding macros.
- Defines bitset, rounding, alignment, min/max, array-size, page rounding, fixed-point, device-block/page conversion, mbuf sizing, byte-order aliases, and variable-length array accessor macros.
- Declares `panic()` for kernel consumers.

Important behavior:
- `MAXBSIZE` is 64 KiB and must be a power of two.
- `MAXPATHLEN` maps to `PATH_MAX`; `MAXSYMLINKS` is 32.
- `PWAKEUP_CPUMASK` limits encoded wakeup CPU IDs and notes a maximum supported CPU count of 16384.
- `MINBUCKET` and `MAXALLOCSAVE` parameterize kernel allocator behavior.
- `MSIZE`, `MCLSHIFT`, and related constants describe mbuf and cluster sizing.

Dependencies:
- Public and kernel consumers include it widely.
- Pulls in `sys/_null.h`, `sys/types.h`, `sys/syslimits.h`, machine headers, and kernel-only `cdefs`, `errno`, and `time`.

Notable risks:
- This is extremely high blast-radius configuration; changing constants affects ABI, VFS, VM, networking, allocator, and userland build assumptions.
- Rounding macros may evaluate arguments multiple times.
- Version macro values gate ports and conditional compatibility code.

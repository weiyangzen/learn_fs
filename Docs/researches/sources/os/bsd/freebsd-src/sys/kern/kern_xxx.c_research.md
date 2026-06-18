# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_xxx.c

## Purpose
Implements legacy FreeBSD/BSD compatibility syscalls for old hostname, hostid, `getkerninfo(2)`, and FreeBSD 4-era `uname(2)`/domain-name ABI surfaces. This is compatibility glue that translates obsolete syscall ABIs onto modern `sysctl`-backed kernel state.

## Key Elements
- `ogethostname()` and `osethostname()` forward old hostname get/set calls to `CTL_KERN.KERN_HOSTNAME`.
- `ogethostid()` and `osethostid()` forward old hostid calls to `CTL_KERN.KERN_HOSTID`.
- `oquota()` is a compatibility stub returning `ENOSYS`.
- `ogetkerninfo()` maps old `KINFO_*` selectors to modern sysctl MIBs for routing, processes, files, VM totals, load average, and clockrate.
- `KINFO_BSDI_SYSINFO` fabricates enough BSDI 1.x-style system information for old BSDI `uname()` consumers.
- `freebsd4_uname()` implements the historical FreeBSD 1.1 binary ABI with fixed `SYS_NMLN == 32` fields.
- `freebsd4_getdomainname()` and `freebsd4_setdomainname()` map old domain-name calls to `KERN_NISDOMAINNAME`.

## Behavior
The compatibility entry points are compiled only under `COMPAT_43` or `COMPAT_FREEBSD4`. Most operations build integer sysctl MIB arrays and call `userland_sysctl()` or `kernel_sysctl()` rather than directly touching global variables. String-returning operations explicitly force trailing NUL bytes in fixed-size legacy structures.

## Filesystem / VM Relevance
The file is not a filesystem implementation, but `ogetkerninfo()` exposes old `KINFO_FILE` and `KINFO_METER` views through `KERN_FILE` and `VM_TOTAL`. These are compatibility inspection paths that can affect old administrative tools observing open files, route tables, and VM totals.

## Locking and Safety
The code delegates synchronization and copyin/copyout validation to sysctl and copy routines. The BSDI compatibility path uses static buffers (`bsdi_si`, `bsdi_strings`) to avoid stack bloat, trims output to the caller's buffer size, and writes back the size value on success.

## Notable Edge Cases
- `ogetkerninfo()` returns the amount needed in `td_retval[0]`, even when the caller buffer is smaller.
- The BSDI sysinfo structure stores string offsets relative to the structure base, not kernel pointers.
- `freebsd4_uname()` synthesizes the legacy `version` field by copying from the first `#` up to `:`.
- The file is entirely ABI compatibility support and should not be used as the model for new syscall design.

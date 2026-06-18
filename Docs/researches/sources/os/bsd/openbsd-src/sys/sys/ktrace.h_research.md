# File Research: sources/os/bsd/openbsd-src/sys/sys/ktrace.h

This header defines ktrace record formats, trace flags, userland syscall prototypes, and kernel trace emitters.

Key definitions:
- Operations: `KTROP_SET`, `KTROP_CLEAR`, `KTROP_CLEARFILE`, `KTROP(o)`.
- Flag: `KTRFLAG_DESCEND`.
- Common record header: `struct ktr_header`.
- Record types: `KTR_START`, `KTR_SYSCALL`, `KTR_SYSRET`, `KTR_NAMEI`, `KTR_GENIO`, `KTR_PSIG`, `KTR_STRUCT`, `KTR_USER`, `KTR_EXECARGS`, `KTR_EXECENV`, `KTR_PLEDGE`, `KTR_PINSYSCALL`.
- Per-record structs: `ktr_syscall`, `ktr_sysret`, `ktr_genio`, `ktr_psig`, `ktr_user`, `ktr_pledge`, `ktr_pinsyscall`.
- Trace facility bits: `KTRFAC_*`, `KTRFAC_MASK`, `KTRFAC_ROOT`, `KTRFAC_INHERIT`.

Userland declarations:
- `ktrace`
- `utrace`

Kernel APIs/macros:
- `KTRPOINT`
- Emitters: `ktrgenio`, `ktrnamei`, `ktrpsig`, `ktrsyscall`, `ktrsysret`, `ktruser`, `ktrexec`, `ktrpledge`, `ktrpinsyscall`, `ktrstruct`.
- Trace state: `ktrcleartrace`, `ktrsettrace`.
- Convenience `ktrstruct` wrappers for timespec/timeval/cmsghdr/fds/fdset/flock/iovec/itimerval/kevent/msghdr/pollfd/quota/rlimit/rusage/sigaction/siginfo/sockaddr/stat.

Risk notes:
- Trace records may include syscall arguments, IO data, exec args/env, pledge failures, and pinsyscall addresses, so output can contain sensitive process data.
- `KTRPOINT` avoids recursive tracing when `P_INKTR` is set.

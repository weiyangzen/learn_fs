# File Research: sources/os/bsd/freebsd-src/sys/sys/ktrace.h

Defines the process ktrace ABI: operations, flags, record headers, record types, facility bits, and kernel/user APIs. `KTROP_SET`, `CLEAR`, and `CLEARFILE` are combined with `KTRFLAG_DESCEND`.

Record headers have legacy timeval and versioned timespec/CPU forms. Record payloads cover syscall entry/return, pathname lookup, generic I/O, processed signals, context switches, user records, named struct dumps, sysctl names, process constructor/destructor, capability failures, page faults, exec args/envs, and extended errors. `KTR_DROP` and `KTR_VERSIONED` are high bits in record type.

Kernel helpers emit each record type, process exec/exit/fork tracing, user-return flushing, structured payloads, capability failures, and raw data. Userland exposes `ktrace()` and `utrace()`.

# File Research: sources/os/bsd/dragonflybsd/sys/sys/ktrace.h

Defines process syscall tracing ABI and kernel helpers. Includes trace operations, trace flags, `ktrace_node`, `ktr_header`, and records for syscall entry/return, generic I/O, signals, and context switches.

Filesystem relevance: `KTR_NAMEI` records pathnames and `KTR_GENIO` records file descriptor read/write data; userland APIs `ktrace()` and `utrace()` expose tracing control. Kernel helpers emit namei, genio, syscall, sysret, sysctl, signal, and context-switch records.

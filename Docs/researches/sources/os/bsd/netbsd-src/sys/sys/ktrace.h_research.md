# File Research: sources/os/bsd/netbsd-src/sys/sys/ktrace.h

Defines the ktrace system call ABI and in-kernel trace record machinery. It includes operation flags, versioned `ktr_header`, record structures for syscall, sysret, namei, genio, signals, context switches, emulation, user records, exec args/env/fd, MIB, and signal masks. It defines trace facility bits, persistent/inherit/emulation/version flags, and user prototypes for `ktrace`, `fktrace`, and `utrace`.

Kernel code gets initialization, reference management, trace emitters, guarded inline wrappers, recursion prevention via `LP_KTRACTIVE`, and entry allocation/addition APIs. Filesystem relevance appears through `KTR_NAMEI`, I/O tracing, and exec argument/environment tracing. Risks include record-version compatibility, trace recursion, data-size limits, and locking around `ktrace_lock`.

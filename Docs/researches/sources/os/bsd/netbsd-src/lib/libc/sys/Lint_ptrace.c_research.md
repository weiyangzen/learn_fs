# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/Lint_ptrace.c

Lint stub for `ptrace(request, pid, addr, data)`. It includes signal/types/ptrace headers for the correct prototype environment and returns zero.

Actual tracing behavior is supplied by the syscall implementation elsewhere.

# File Research: sources/os/bsd/openbsd-src/sys/sys/stacktrace.h

Fixed-size kernel stacktrace capture ABI.

This header defines `STACKTRACE_MAX` as 19 program counters and `struct stacktrace` with a count and PC array. Kernel builds expose printing, capture at a skip depth, user-trace capture, and an inline `stacktrace_save()` wrapper.

Filesystem/storage relevance: diagnostic only. It can support lock, allocation, or error tracing in filesystem and storage code, but it contains no VFS policy.

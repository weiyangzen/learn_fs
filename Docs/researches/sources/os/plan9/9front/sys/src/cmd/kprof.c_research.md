# File Research: sources/os/plan9/9front/sys/src/cmd/kprof.c

`kprof` reads a kernel text image and a binary profiling data file, attributes tick counts to text symbols, sorts by time, and prints milliseconds/percentage/function.

It uses `<mach.h>` to parse the executable header, initialize symbols, and iterate text symbols. The data file is interpreted as big-endian `ulong` counters: total ticks, outside-kernel ticks, then address-indexed samples relative to kernel text base. It warns if `mach->kbase` differs from the first text symbol page.

The implementation is intentionally simple and assumes profiling data shape matches the kernel’s expected layout.

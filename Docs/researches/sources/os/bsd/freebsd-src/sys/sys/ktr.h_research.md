# File Research: sources/os/bsd/freebsd-src/sys/sys/ktr.h

Kernel trace ring-buffer support. `struct ktr_entry` records timestamp, CPU, source line/file, description format, thread, and six parameters. Globals define CPU mask, runtime mask, entry count, verbosity, ring index, and buffer pointer.

When `KTR` is compiled in, `CTR0` through `CTR6` macros emit tracepoints if the compile-time class mask includes the class. Without `KTR`, they compile away. `TR*` aliases target the general class.

The file also defines graph-oriented event macros for schedgraph-style state, counter, point, start, and stop events with up to four attributes, plus `ITR*` init-trace macros that are fully omitted unless `KTR_INIT` is compiled.

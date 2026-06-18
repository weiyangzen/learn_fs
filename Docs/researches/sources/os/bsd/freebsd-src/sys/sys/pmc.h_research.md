# File Research: sources/os/bsd/freebsd-src/sys/sys/pmc.h

This is the main FreeBSD hwpmc ABI and kernel-private state header. It includes event definitions, process/counter/machine-dependent PMC headers, and, in kernel builds, epoch and CK queue support. It defines module name, name/class limits, ABI version `0x0A010000`, and a CPU model string buffer.

Large macro tables enumerate supported CPU types and PMC classes, preserving sparse numeric assignments for ABI stability. Other enums define PMC hardware/software states, operating modes (system/thread and sampling/counting combinations), row dispositions, capabilities, and event numbers generated from `pmc_events.h`. Helper macros test mode categories and encode/decode `pmc_id_t` fields for CPU, mode, class, and row index.

The user/kernel syscall interface is described by `enum pmc_ops` and operation structs for configure/flush/close log, CPU info, driver stats, PMC info, admin, allocate, attach/detach, get MSR, release, read/write, set count, start/stop, write log, dynamic event info, and capability lookup. Allocation carries requested caps, CPU, class, event, flags, mode, initial/sample count, returned id, and MD extension union.

Kernel-only sections define driver sizing constants, locking annotations, syscall argument wrapper, human-readable PMC descriptors, target/process/thread/owner tracking, hardware PMC rows, sample buffers, multipart payloads, per-CPU PMC state, CPU binding state, class-dependent method vectors, and machine-dependent dispatch vectors. Debug builds wire a detailed KTR-based tracing macro family by subsystem/minor category. The header declares MD initialization/finalization, interrupt processing, callchain capture, CPU binding, class allocation, and timestamp helpers.

Filesystem relevance is mostly observability: hwpmc can profile kernel and user execution, including VFS/filesystem hot paths, block I/O stacks, and cache behavior. Its ABI stability and binary log compatibility are important for profiling tools.

# File Research: sources/os/bsd/freebsd-src/sys/sys/pmclog.h

This header defines the binary log record ABI produced by hwpmc. It includes `sys/pmc.h`, enumerates log record types, declares packed record layouts, provides header bitfield helpers, and exposes kernel log-processing prototypes.

`enum pmclog_type` preserves versioned ABI additions: V1 records for close/drop/init/allocate/attach/detach/context switch/exec/exit/fork/sys exit/user data, V2 map-in/map-out/callchain replacements, V3 dynamic allocation, and V6 thread/process creation records. Each record begins with a common header containing a 32-bit packed magic/type/length header, spare field, and 64-bit timestamp counter.

Packed structs define payloads for callchains, initialization, mappings, PMC allocation, attach/detach, process context switch, process create/exec/exit/fork, syscall exit, thread create/exit, user data, and dynamic allocation. Callchain CPU/mode flags and multipart callchain payload tags are defined. `union pmclog_entry` sizes scratch areas for all record variants.

Header macros extract length, type, and magic from a record header and validate the `0xEE` magic. Kernel prototypes configure/deconfigure/flush/close logs and enqueue/process all record types. Filesystem relevance is observability and tooling: profiler logs include executable mappings and paths, which are crucial for attributing sampled time to filesystem and storage code paths.

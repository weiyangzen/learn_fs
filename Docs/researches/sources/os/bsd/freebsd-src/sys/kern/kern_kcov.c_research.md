# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_kcov.c

## Purpose
Implements the `/dev/kcov` kernel coverage tracing device used by fuzzing and testing tools to collect per-thread program-counter or comparison coverage.

## Main Elements
- `struct kcov_info` tracks the traced thread, physical VM object, kernel mapping, entry count/size, state, and trace mode.
- State machine: `OPEN` after device open, `READY` after buffer allocation, `RUNNING` while probes record into the buffer, and `DYING` after close cleanup begins.
- `get_kinfo()` filters tracing to the current non-interrupt thread with a running KCOV state.
- `trace_pc()` stores return addresses in PC mode; `trace_cmp()` stores type/arg/return comparison tuples in CMP mode.
- `kcov_open()` allocates per-fd state and installs cdevpriv cleanup.
- `kcov_close()` rejects closing while tracing is still running.
- `kcov_mmap_single()` exposes the allocated buffer object read/write but not executable.
- `kcov_alloc()` allocates wired physical pages, maps them in KVA, and prepares a VM object sized/aligned for mmap.
- `kcov_ioctl()` implements `KIOSETBUFSIZE`, `KIOENABLE`, and `KIODISABLE`, registering/unregistering global coverage callbacks as active users appear/disappear.
- `kcov_thread_dtor()` disables tracing and frees or returns buffers to READY on thread exit.
- Sysinit creates `/dev/kcov` mode `0600` and registers the thread destructor.

## Dependencies And Integration
Integrates with sanitizer/coverage compiler hooks (`cov_register_pc`, `cov_register_cmp`), devfs cdevpriv, VM objects/pages/radix, pmap KVA mappings, thread destructor eventhandler, and `kern.kcov.max_entries` sysctl.

## Risk Notes
Memory ordering is explicit around transitions into and out of `RUNNING`, because instrumentation can fire from difficult contexts. The implementation avoids tracing interrupts and uses a spin mutex plus atomics for global callback registration. VM object cleanup must unwind wired pages and KVA mappings exactly once, including close-vs-thread-exit races.

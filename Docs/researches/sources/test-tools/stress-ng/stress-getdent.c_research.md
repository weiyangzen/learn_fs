<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-getdent.c -->
# sources/test-tools/stress-ng/stress-getdent.c Research

Purpose: implements `getdent`, a filesystem/OS stressor that directly exercises Linux `getdents` and/or `getdents64` syscalls while recursively walking common system directories.

Important APIs/types/functions: `stress_getdents_func` abstracts old and 64-bit getdents readers. `getdents_funcs[]` holds compiled syscall variants. `stress_getdents_rand()` selects a variant randomly and disables it if it returns ENOSYS. `stress_getdents_dir()` and `stress_getdents64_dir()` open a directory, allocate a page-aligned-ish random buffer, issue invalid bad-fd and zero-size calls, then read entries and optionally recurse. `stress_gendent_offset()` performs byte-offset pointer movement.

Control flow: `stress_getdent()` synchronizes, then repeatedly scans `/proc`, `/dev`, `/tmp`, `/sys`, and `/run` with different recursion depths. Each directory reader opens the path, allocates a random buffer up to 256 KiB plus page rounding, times syscall calls, increments count and bogo operations for successful reads, walks returned records safely using `d_reclen`, and recurses into non-dot directories. On exit it reports nanoseconds per getdents call.

State and persistence: function pointers in `getdents_funcs[]` can be nulled after ENOSYS for the process lifetime. All buffers are heap-local and freed per directory call. No filesystem changes are made.

Dependencies and integration: depends on Linux syscall numbers, stress-ng getdents shims and dirent structs, bad-fd helper, filesystem path helpers, random buffer sizing, timing, metrics, sync/state, and verify registration.

Risks: direct parsing of kernel dirent records must guard bad `d_reclen`; the code breaks out on invalid records. Recursion over live pseudo-filesystems can race with disappearing directories. A negative errno is returned internally but the top-level stressor ultimately returns success unless no syscall variant remains.

Test signals: metric output is nanoseconds per getdents call. Failure logs occur when all syscall variants fail unexpectedly. Test on Linux architectures with only getdents64, with inaccessible pseudo-filesystem directories, and under concurrent filesystem churn.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-getdent.c -->

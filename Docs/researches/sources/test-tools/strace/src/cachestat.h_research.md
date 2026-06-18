<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/cachestat.h -->
## sources/test-tools/strace/src/cachestat.h

Purpose: Defines tracee-facing layouts for the `cachestat` syscall range and result structures.

Important APIs and types: `struct cachestat_range` has `uint64_t off` and `len`. `struct cachestat` has five `uint64_t` counters.

Control flow: Header-only; consumed by `cachestat.c`.

State and persistence: No state.

Dependencies and integration: Includes `<stdint.h>` and is local to strace's cachestat decoder.

Risks: Layout must track kernel UAPI exactly. Any new fields or type changes require synchronized decoder updates.

Test signals: Compile layout checks and cachestat syscall output tests validate this header indirectly.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/cachestat.h -->

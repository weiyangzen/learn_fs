# sources/test-tools/stress-ng/stress-mmaphuge.c

Purpose: implements the `mmaphuge` VM stressor. It tries large anonymous and optional file-backed mappings with explicit huge-page flags and transparent huge-page-friendly sizes, touches and validates sparse strides, and then unmaps whole or partial huge mappings.

Important APIs/types/functions: `stress_mmaphuge_context_t` holds mapping descriptors, options, file descriptor, NUMA masks, and mmap stats. `stress_mmaphuge_setting_t` enumerates `MAP_HUGETLB`, huge-size encodings, and THP fallback sizes. `stress_mmaphuge_child()` performs mapping/touching/unmapping; `stress_mmaphuge()` prepares shared context, optional backing file, NUMA settings, OOM wrapper, metrics, and cleanup.

Control flow: setup allocates shared context plus the buffer descriptor array, optionally creates an unlinked 16 MiB temp file with `fallocate()`, and resolves `mmaphuge-mmaps`, `mmaphuge-file`, `mmaphuge-mlock`, and `mmaphuge-numa`. The child cycles through mapping settings, attempting file-backed maps before anonymous maps, checks low-memory conditions, writes and verifies sparse 64-page strides, optionally randomizes NUMA placement and mlocks mappings, toggles THP advice, gathers mmap stats, then tries partial end-page/start-range unmaps before force-unmapping the whole range if needed.

State and persistence: shared state is the context and accumulated `stress_mmap_stats_t`; filesystem state is an unlinked temporary file and temp directory removed at exit. Huge mappings are transient and are explicitly unmapped.

Dependencies and integration: gated by `MAP_HUGETLB`; integrates core mmap stats, NUMA helpers, OOM child execution, temp-file helpers, mlock, madvise, memory usage reporting, and stressor metrics.

Risks and test signals: huge-page availability is host-configuration-dependent, partial unmaps may fail on true huge pages, and file-backed huge maps can fail by filesystem/kernel policy. Useful signals are graceful skips on unsupported builds/resources, verified sparse contents, nonzero bogo operations, mmap stats reports, and cleanup of file descriptors/directories.

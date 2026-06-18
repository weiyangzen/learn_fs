# sources/test-tools/stress-ng/stress-mmaptorture.c

Purpose: implements `mmaptorture`, a VM stressor that performs aggressive file-backed, anonymous, and POSIX shared-memory mapping churn with random offsets, sizes, advice, sync, protection changes, locking, remapping, forked cleanup, and signal recovery.

Important APIs/types/functions: `mmap_info_t` records active mappings, and `mmap_stats_t` accumulates page-level counters. Global `mmap_fd`, `mmap_data`, `mmap_bytes`, and shared `mmap_stats` support init/deinit and child execution. `stress_mmaptorture_init()` creates and maps the backing file, `stress_mmaptorture_child()` performs the torture loop, `stress_mmaptorture_sighandler()` recovers from SIGBUS/SIGSEGV via `siglongjmp`, and `stress_mmaptorture_msync()` probabilistically syncs pages.

Control flow: init sizes the backing file per instance, creates an unlinked temp file, truncates it, and maps the whole region. The child allocates scratch buffers and mapping slots, installs signal handlers, then repeatedly truncates/restores the backing file, writes through the primary map, optionally remaps file pages, creates up to 128 secondary mappings, applies random `fallocate`/hole-punch, file/SHM/anonymous mapping choices, VMA names, prefetch, NUMA movement, madvise, mincore, mlock, mprotect, msync, fixed-address negative tests, and occasional early unmaps. It may fork a child that mlockalls, drops advice, seals one mapping, and unmaps inherited mappings. Cleanup remaps smaller via `mremap`, resets advice/protection, unlocks, optionally removes pages, and advances backing-file offsets.

State and persistence: persistent state includes the unlinked temp file, global primary mapping, and shared stats until deinit. Secondary mappings and POSIX shm names are transient. Stats are reported as rates for mapped, synced, locked, protected, advised, remapped, retry, SIGBUS, and SIGSEGV pages.

Dependencies and integration: requires `siglongjmp`; optionally uses POSIX shm, `remap_file_pages`, `mremap`, NUMA, mlockall, mseal, fallocate hole punching, mincore, VMA naming, OOM wrapper, and stress-ng temp-file lifecycle.

Risks and test signals: the stressor intentionally triggers SIGBUS/SIGSEGV-prone races with truncated files and changing protections. Useful signals are recovered traps, page-rate metrics, absence of leaked child processes, cleanup of temporary directories, and graceful skip when initial mapping or signal support is unavailable.

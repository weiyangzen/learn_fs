# sources/test-tools/stress-ng/stress-msync.c

Purpose: implements `msync`, a VM/filesystem stressor that checks synchronization between a shared file mapping and its backing file in both writeback and invalidate directions, while also exercising invalid `msync()` calls.

Important APIs/types/functions: `stress_page_check()` verifies a page is filled with an expected byte pattern. `stress_sigbus_handler()` counts SIGBUS and returns through `siglongjmp`. `stress_msync()` sizes the mapped file, creates an unlinked temp file, maps it shared, maps a scratch read buffer, runs MS_SYNC/MS_INVALIDATE checks, and handles cleanup.

Control flow: setup installs SIGBUS recovery, resolves `msync-bytes`, creates a temp file, truncates it, maps the full region shared, and maps a one-page anonymous read buffer. Each loop picks a page-aligned offset, writes a random byte pattern in memory, calls `MS_SYNC`, reads the file, and verifies persisted data. It then writes another pattern, reads file data, calls `MS_INVALIDATE`, and verifies memory contents. It also probes invalid flag combinations, wrap-around addresses, zero-length no-op, and locked-page invalidate behavior.

State and persistence: filesystem state is an unlinked temp file and temp directory removed at exit. Static SIGBUS count persists for the process and is reported. Mappings are explicitly unmapped.

Dependencies and integration: requires `msync()`; uses stress-ng mmap populate, temp-file helpers, OOM adjustment, settings, memory usage reporting, shim msync/mlock/munlock, signal helpers, and verification.

Risks and test signals: filesystem semantics and FreeBSD behavior differ, SIGBUS can occur if backing storage changes, and `MS_INVALIDATE` on locked pages may return EBUSY. Signals are successful page comparisons, bogo increments, reported SIGBUS count if any, and cleanup of fd/mappings/temp directory.

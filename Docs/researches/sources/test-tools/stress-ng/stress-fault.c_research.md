# sources/test-tools/stress-ng/stress-fault.c

Purpose: implements `fault`, a page-fault stressor that creates major faults through tiny file-backed mappings and minor faults through remapped anonymous pages, then reports fault rates when `getrusage()` exposes counters.

Important APIs/types/functions: `stress_segvhandler()` uses `siglongjmp` to escape unexpected SIGSEGV/SIGBUS. `stress_fault()` coordinates temp-file creation, mmap/fallocate/write, unlink timing, `madvise()` fault forcing, resource usage metrics, and cleanup.

Control flow: setup creates a temp directory and filename, installs SIGSEGV/SIGBUS handlers, maps a read-only page placeholder, sync-starts, and loops. Each iteration opens/creates the temp file, ensures it has one byte via `posix_fallocate()` or write, sometimes unlinks it before mapping, maps one byte shared writable, writes through the mapping to fault it in, optionally applies `MADV_DONTNEED` and `MADV_PAGEOUT` and writes again, unmaps, unlinks when needed, then tries a minor fault path by remapping and reading from an anonymous page.

State and persistence behavior: temporary file state is created and removed under stress-ng temp directories. Runtime state includes signal jump flags, fault timing/count accumulators, resource usage snapshots, and one anonymous mapping. No durable state remains after cleanup.

Dependencies and integration points: requires `siglongjmp`; optionally uses `getrusage`, `posix_fallocate`, `madvise`, and `MADV_PAGEOUT`. Integrates with stress-ng executable text address, temp-file, mmap force-unmap, signal, put, process-state, and metrics helpers. Classifier is `CLASS_INTERRUPT | CLASS_OS`.

Risks: page-fault behavior varies by filesystem, memory pressure, and kernel VM policy. Mapping a one-byte file then naming the mapping with page size relies on page granularity. Unexpected SIGBUS/SEGV is treated as failure, while ENOSPC/ENOMEM capacity errors are retried.

Test signals: run on disk-backed and tmpfs temp locations, check major/minor fault debug output, verify `nanosecs per page fault` metrics where supported, and interrupt runs to confirm temp files are unlinked.

# sources/test-tools/stress-ng/stress-munmap.c

Purpose: implements `munmap`, a Linux VM stressor that parses the child process map list and unmaps eligible file-backed readable non-executable pages in a prime-stride order to create many VMA holes.

Important APIs/types/functions: `munmap_context_t` stores args, page shift, executable path, and timing counters. `stress_munmap_log2()` computes page-size shift, `stress_munmap_stride()` finds a prime stride, `stress_munmap_range()` unmaps pages and checks residency with `mincore`, `stress_munmap_child()` filters `/proc/$pid/maps`, and `stress_munmap()` runs repeated OOMable children.

Control flow: the parent allocates shared context, resolves `/proc/self/exe`, synchronizes, and repeatedly starts `stress_munmap_child()` through `stress_oomable_child()`. The child installs SIGSEGV/SIGBUS exit handlers, opens `/proc/$pid/maps`, optionally marks mappings `MADV_DONTDUMP` and pageout under aggressive mode, rewinds, then filters out anonymous, special, libc, `/dev/zero`, executable, non-readable, stress-ng executable, args, and context ranges. For eligible ranges it unmaps each page using a prime stride and records timing/count metrics.

State and persistence: shared context persists across child runs; child unmaps only its own address space. No filesystem state is modified beyond reading proc files.

Dependencies and integration: Linux-only; uses proc maps parsing, prime helper, mincore, mmap shared context, signal exit handlers, OOM wrapper, proc self exe helper, metrics, and bogo counters.

Risks and test signals: bad filtering can unmap critical libraries or data and crash the child, which is contained by the OOMable child boundary and signal handlers. Signals are successful child iterations, nanoseconds-per-page metrics, bogo increments, and no mincore evidence that unmapped pages remain resident.

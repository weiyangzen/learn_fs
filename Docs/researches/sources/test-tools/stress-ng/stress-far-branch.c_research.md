# sources/test-tools/stress-ng/stress-far-branch.c

Purpose: implements `far-branch`, a CPU/cache stressor that fills many memory pages with return opcodes, spreads callable function pointers across the address space, and repeatedly calls them to stress branch prediction, instruction cache, TLB, and executable mapping behavior.

Important APIs/types/functions: options `far-branch-pages`, `far-branch-flush`, and `far-branch-pageout` control scale and cache/pageout behavior. `stress_far_try_mmap()` and `stress_far_mmap()` map executable return pages at varied addresses and sometimes remap from a backing file. `stress_far_branch_shuffle()`, `stress_far_branch_page_flush()`, `stress_far_branch_pageout()`, and `stress_far_branch()` implement function generation and call loops.

Control flow: setup creates an unlinked temp backing file, installs SIGILL/SIGSEGV/SIGBUS handlers with `sigsetjmp`, allocates function and page arrays, maps pages at offsets from the stressor or random fixed addresses, writes architecture-specific return opcodes, mprotects pages executable, and records function pointers. The loop calls functions in unrolled groups of 32, tracks call count, optionally flips bytes and flushes instruction cache, optionally pageouts/offlines random pages and local labels, periodically shuffles pointer order, and emits call-rate metrics.

State and persistence behavior: executable pages are anonymous or file-backed mappings; the backing file is unlinked and removed with the temp directory. State includes signal diagnostics, `check_flag`, function pointer arrays, mapped page pointers, and call metrics. Cleanup unmaps pages and closes the file.

Dependencies and integration points: requires `mprotect()` and supported return-opcode assembly, excluding NetBSD mitigation paths. Uses stress-ng arch, ret-opcode, cacheflush, madvise, mmap, temp-file, process-state, metrics, and signal helpers.

Risks: executable writable mappings, fixed-address attempts, file-backed executable mappings, and pageout/offline requests are highly platform and policy dependent. Bad return opcodes or stale icache flush behavior can produce SIGILL/SIGSEGV/SIGBUS; handlers convert this into controlled cleanup. Mapping failure fallback duplicates successful page pointers, so cleanup must tolerate aliases carefully.

Test signals: run default, `--far-branch-pages 1`, `--far-branch-flush`, and `--far-branch-pageout`; confirm nonzero calls/sec, check function executed, no duplicate-unmap failures, and unimplemented reporting on unsupported architectures or hardened kernels.

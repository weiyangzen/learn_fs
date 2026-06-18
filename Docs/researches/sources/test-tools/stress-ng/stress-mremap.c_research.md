# sources/test-tools/stress-ng/stress-mremap.c

Purpose: implements `mremap`, a VM stressor that repeatedly shrinks and expands anonymous mappings, optionally moving them to fixed addresses, locking pages, randomizing NUMA placement, and verifying retained page contents.

Important APIs/types/functions: `rand_mremap_addr()` reserves and frees a random destination for `MREMAP_FIXED`. `try_remap()` wraps `mremap()` retry logic, timing metrics, optional `MREMAP_DONTUNMAP`, and optional mlock. `stress_mremap_child()` handles allocation, shrink/expand loops, advice, mincore touching, verification, invalid remap calls, and metrics. `stress_mremap()` runs the child under the OOM wrapper.

Control flow: the child computes per-instance `mremap-bytes`, enables optional `MAP_POPULATE`, resolves `mremap-mlock` and `mremap-numa`, then synchronizes. Each iteration maps the current maximum size, optionally NUMA-randomizes, applies random/mergeable advice, touches pages, verifies initial patterns, repeatedly halves the mapping down to one page, then doubles it back toward the target size. It tests invalid flags, invalid fixed destination, and zero new size before force-unmapping.

State and persistence: all state is process-local anonymous memory plus optional NUMA masks and accumulated timing/count metrics. No filesystem state is created.

Dependencies and integration: requires `mremap()` and glibc 2.4-compatible support; optionally uses `MREMAP_FIXED`, `MREMAP_DONTUNMAP`, mlock, NUMA helpers, mincore, madvise helpers, OOM wrapper, memory usage reporting, and verification flags.

Risks and test signals: address-space fragmentation and low memory can cause retries; `MREMAP_FIXED` support varies. Verification detects data loss across remaps. Signals are nanoseconds-per-call metrics, bogo increments per full shrink/expand cycle, no leaked mapping on stop, and graceful unimplemented/resource handling.

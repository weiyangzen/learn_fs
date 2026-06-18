# sources/test-tools/stress-ng/stress-pagemove.c

Purpose: `stress-pagemove.c` implements the `pagemove` stressor, using Linux `mremap(MREMAP_FIXED | MREMAP_MAYMOVE)` to rotate physical page mappings through virtual addresses and verify that page contents move as expected.

Important APIs/types/functions: `page_info_t` records the original virtual address and page number stored at each page. `stress_pagemove_info_t` carries parsed byte count, page count, mlock, and NUMA settings. `stress_pagemove_child()` performs the moving and verification. `stress_pagemove_remap_fail()` reports failed remaps.

Control flow: the top-level function resolves `pagemove-bytes`, scales it per instance, aligns to page size, enforces at least three pages and a 32-bit-safe maximum, reports memory use, and invokes an oomable child. The child mmaps one extra page, optionally mlocks, unmaps the extra page as a swap slot, optionally prepares NUMA masks, then loops: writes page identity records, protects the region read-only, verifies identities, and for each adjacent pair moves the current page to the unmapped slot, the next page down, and the slot page back up. It periodically records remap timing metrics and validates the final rotated page numbers.

State and persistence behavior: all state is anonymous memory plus optional NUMA placement and mlock state. The extra page is intentionally unmapped to provide a temporary fixed remap target. Cleanup unmaps the main region and frees NUMA masks.

Dependencies and integration points: it requires `mremap` with fixed/maymove flags, `mprotect`, stress-ng mmap/oom/memory accounting, optional `mlock`, optional Linux NUMA helpers, and registers as `CLASS_VM | CLASS_OS` with `VERIFY_ALWAYS`.

Risks: fixed remaps are sensitive to alignment and mapping holes; any failed intermediate remap can leave parts of the original region moved, so cleanup uses broad unmap attempts. NUMA randomization mutates the shared `pagemove_numa` flag inside child context. Verification assumes every page can hold `page_info_t`.

Test signals: `--pagemove` should report bogo progress and `page remaps per sec`. Variants should include `--pagemove-mlock`, `--pagemove-numa`, tiny byte values that force minimum adjustment, large byte values that force maximum adjustment, and unsupported builds without `mremap` flags.

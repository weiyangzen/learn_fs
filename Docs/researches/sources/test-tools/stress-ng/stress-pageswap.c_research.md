# sources/test-tools/stress-ng/stress-pageswap.c

Purpose: `stress-pageswap.c` implements the `pageswap` stressor, allocating one page at a time and asking the kernel to page it out with `madvise(MADV_PAGEOUT)` before later touching and unmapping the list.

Important APIs/types/functions: `page_info_t` embeds `self`, `next`, and `size` in each mapped page for list walking and verification. `stress_pageswap_supported()` gates on `MADV_PAGEOUT`. `stress_pageswap_count_paged_out()` optionally uses `mincore()` to count nonresident pages. `stress_pageswap_unmap()` pages out, verifies, counts, and unmaps the list. `stress_pageswap_child()` performs the allocation/pageout loop.

Control flow: `stress_pageswap()` resolves `pageswap-pages`, reports memory use, synchronizes, and runs an oomable capability-dropping child. The child maps private anonymous pages, links them into a list, stores self pointers, calls `MADV_PAGEOUT` on the new and previous head, optionally repopulates reads in aggressive mode, and unmaps the whole list when the configured page count or memory-low condition is reached. Bogo ops increment on each successful page mapping.

State and persistence behavior: state is only anonymous page mappings linked through in-page metadata. No files are created. Verification reads back `self` before unmapping; this intentionally faults pages back in after pageout.

Dependencies and integration points: it depends on Linux `MADV_PAGEOUT`, optional `MADV_POPULATE_READ`, optional `mincore`, stress-ng OOM child handling, memory-low checks, sync barriers, metrics, and `CLASS_OS | CLASS_VM` registration with `VERIFY_OPTIONAL`.

Risks: `MADV_PAGEOUT` is advisory, so mincore counts can vary with kernel memory pressure and policy. The stressor can create many VMAs and provoke reclaim; OOM avoidance is important under constrained memory. Verification only checks page metadata after reaccess, not that the kernel actually swapped the page.

Test signals: direct `--pageswap` runs should produce bogo progress and possibly `microsecs per page swapout`. Useful variants include `--pageswap-pages 1`, maximize pages, aggressive mode, verify mode, and systems without `MADV_PAGEOUT` where the supported callback must skip cleanly.

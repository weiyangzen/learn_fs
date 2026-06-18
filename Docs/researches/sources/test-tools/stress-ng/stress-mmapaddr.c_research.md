# sources/test-tools/stress-ng/stress-mmapaddr.c

Purpose: `stress-mmapaddr.c` stresses mapping at randomly chosen virtual addresses. It searches for apparently unmapped addresses using `mincore`, maps pages with random fixed/locked/populated options, validates residency, remaps or maps again, and tests `MAP_FIXED_NOREPLACE`.

Important APIs/types/functions: `page_fault` and `stress_fault_handler` detect unexpected SIGSEGV on mapped-page reads. `stress_mmapaddr_check` reads the page and verifies `mincore` residency. `stress_mmapaddr_get_addr` repeatedly samples page-aligned addresses under either 32-bit or full pointer masks until `mincore` reports `ENOMEM`, meaning unmapped. `stress_mmapaddr_child` owns the OOM-contained loop.

Control flow: `stress_mmapaddr` installs a SIGSEGV handler and runs `stress_oomable_child`. The child reads `--mmapaddr-mlock`, synchronizes, then repeatedly chooses a random address mask, finds an unmapped address, builds mmap flags, checks OOM avoidance, maps one read-only page at or near the address, applies mergeable advice and optional mlock, checks it, optionally maps/remaps another page, uses `mremap(MREMAP_FIXED | MREMAP_MAYMOVE)` to move the original page to a fresh address when supported, attempts a `MAP_FIXED_NOREPLACE` mapping over an existing address to force failure, unmaps, and increments bogo operations.

State and persistence behavior: all state is anonymous memory and the process-local `page_fault` flag. No files are created. The stressor expects transient mappings and force-unmaps all successful pages.

Dependencies and integration points: the file uses core madvise, mmap, OOM helpers, `shim_mincore`, optional `mremap`, `MAP_32BIT`, `MAP_FIXED_NOREPLACE`, and `mlock`. It registers `CLASS_VM | CLASS_OS`, `VERIFY_ALWAYS`, and the `--mmapaddr-mlock` option.

Risks: address-space layout and kernel overcommit policies can make random address sampling noisy. `mincore` may be unavailable (`ENOSYS`), causing the loop to stop. A global SIGSEGV handler can mask unexpected faults if not scoped carefully. Fixed mappings are inherently risky, but the file checks occupancy before use.

Test signals: run `stress-ng --mmapaddr 1 --mmapaddr-ops 1 --verify`, repeat with `--mmapaddr-mlock`, and test on systems with/without `MAP_FIXED_NOREPLACE` and `mremap`. Unexpected SIGSEGV or failed `mincore` on a mapped page should fail verification.

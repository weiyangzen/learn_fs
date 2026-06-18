# sources/test-tools/stress-ng/stress-physpage.c

Purpose: `stress-physpage.c` implements the Linux `physpage` stressor, translating virtual pages through `/proc/self/pagemap`, checking `/proc/kpagecount`, and optionally exercising `/dev/mem` and MTRR operations for the resulting physical page.

Important APIs/types/functions: `PAGE_PRESENT` and `PFN_MASK` decode pagemap entries. `stress_physpage_supported()` requires `CAP_SYS_ADMIN`. `stress_virt_to_phys()` does the virtual-to-physical lookup, kpagecount validation, `/dev/mem` read/mmap attempts, optional writable mapping, and optional MTRR exercise. On x86 with MTRR headers, `stress_physpage_mtrr()` adds, verifies, and deletes MTRR entries for several cache types.

Control flow: the stressor opens `/proc/self/pagemap`, optionally `/proc/kpagecount`, and optionally `/dev/mem`, then synchronizes. Each iteration maps one private writable page near an incrementing preferred address, names it, translates it, unmaps it, also translates `g_shared->stats`, increments bogo ops, and continues while no hard verification failure occurs.

State and persistence behavior: state is transient anonymous page mappings plus open proc/dev descriptors. Optional MTRR modification touches kernel-wide MTRR state but deletes entries after each successful add. No normal files are created.

Dependencies and integration points: Linux proc pagemap interfaces, `/dev/mem`, x86 MTRR ioctls, stress-ng capability checks, mmap helpers, shared stats pointer, and `CLASS_VM` registration with `VERIFY_ALWAYS`.

Risks: pagemap PFNs are privileged and can be masked or restricted; `/proc/kpagecount` and `/dev/mem` may be absent or denied. MTRR operations are global and platform-specific, so `--physpage-mtrr` is risky and should be privileged-only. A zero physical address is treated as nonfatal.

Test signals: `--physpage` should skip without `CAP_SYS_ADMIN`; privileged runs should bogo-progress while kpagecount is sane. Additional signals include debug messages when `/proc/kpagecount` is unavailable, `/dev/mem` denial tolerance, and MTRR add/get/delete behavior under `--physpage-mtrr`.

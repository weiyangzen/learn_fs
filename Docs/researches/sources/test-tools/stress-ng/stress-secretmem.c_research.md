# sources/test-tools/stress-ng/stress-secretmem.c

Purpose: implements `secretmem`, a Linux secret-memory stressor that uses `memfd_secret()` to allocate secretmem-backed mappings, punches holes by unmapping pages, and repeats under OOM-safe child handling.

Important APIs/types/functions: `secretmem_mapping_t` tracks a three-page mapping and bitmap of live pages. `stress_secretmem_supported()` probes `shim_memfd_secret(0)` and distinguishes ENOSYS from unreserved secretmem ENOMEM. `stress_secretmem_unmap()` unmaps first/third pages, then the middle page, updating bitmaps. `stress_secretmem_child()` owns the mapping loop. `stress_secretmem_info` sets a support probe and `CLASS_CPU`.

Control flow: `stress_secretmem()` runs the child through `stress_oomable_child()` quietly. The child allocates the mapping table, opens a secretmem fd, truncates it to `MAPPINGS_MAX * 3` pages, synchronizes, then loops mapping three-page windows at increasing offsets. For each mapping it optionally stops on low memory, marks all pages live, marks memory mergeable, touches all pages to allocate secret pages, unmaps the middle page to create a hole, increments bogo, and later calls `stress_secretmem_unmap()` for all touched mappings before repeating.

State and persistence: state is a secretmem fd, transient shared mappings, and an in-memory bitmap table. The fd is closed and the table freed on exit. No durable files are created.

Dependencies and integration points: requires Linux `__NR_memfd_secret`. It integrates with stress-ng OOM child handling, mmap force-unmap, madvise, low-memory checks, sync, and bogo counters.

Risks and test signals: secretmem requires kernel support and boot-time reserved memory, so skips are common. OOM behavior is intentional when secret pages are exhausted. Signals are support-probe skip messages, bogo increments per mapped/hole-punched region, and complete unmapping/close/free cleanup.

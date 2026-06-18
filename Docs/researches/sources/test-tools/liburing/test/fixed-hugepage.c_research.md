<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/fixed-hugepage.c -->
## sources/test-tools/liburing/test/fixed-hugepage.c

Purpose: tests registered fixed buffers backed by huge pages, multi-size THP-like allocations, unaligned hugepage offsets, and mixed huge/small page mappings.

Important APIs/types/functions: `mmap_hugebufs`, `mmap_mixture`, `get_mthp_bufs`, `register_submit`, `do_read`, `do_write`, `io_uring_register_buffers`, `io_uring_prep_read_fixed`, `io_uring_prep_write_fixed`, `MAP_HUGETLB`, and `MTHP_16KB`.

Control flow: `main` opens an input file or `/dev/urandom` plus `/dev/zero`, creates a ring, then runs one-hugepage, multi-hugepage, unaligned hugepage, unaligned multi-size-page, and two mixed huge/small page scenarios. Each scenario registers buffers, performs fixed read and fixed write, unregisters, and unmaps/frees memory.

State and persistence behavior: each scenario maps or allocates memory and registers it as fixed buffers. Mappings are explicitly unmapped or freed after use.

Dependencies and integration points: depends on hugepage availability, THP/mTHP configuration, memlock limits, and fixed-buffer pinning.

Risks: many environments skip due to missing hugepages or `-ENOMEM`/`-EINVAL`. Mixed mappings target coalescing bugs.

Test signals: pass means fixed buffer registration and IO handle huge and mixed page-backed memory correctly.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/fixed-hugepage.c -->

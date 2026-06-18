<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/memfd_create.c -->
# sources/test-tools/strace/src/memfd_create.c

Purpose: decodes `memfd_create` name and flags, including hugetlb page-size encoding.
Important APIs/types/functions: `SYS_FUNC(memfd_create)`, `printpath`, `memfd_create_flags`, `MAP_HUGE_SHIFT`, and huge-page size extraction.
Control flow: prints name string, known flags, unknown bits, and optional huge-page size shift comment/value. State and persistence behavior: stateless; returns fd through syscall return flags.
Dependencies and integration points: file-descriptor syscall decoding and Linux memfd constants. Risks: huge flag encoding overlaps generic flags and needs masking order. Test signals: normal memfd, sealing, hugetlb, huge size, and unknown flag tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/memfd_create.c -->

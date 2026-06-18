# File Research: sources/os/linux/linux-stable/fs/tests/binfmt_elf_kunit.c

Purpose: KUnit tests for ELF loader mapping-size calculation.

Key responsibilities:
- Tests `total_mapping_size()` with no headers, empty headers, non-`PT_LOAD` headers, real-world `/bin/mount`-like program headers, and unordered `PT_LOAD` headers.
- Verifies that mapping size is based on loadable segments and is order-independent.

Important interactions:
- Uses KUnit suite registration through `kunit_test_suite()`.
- Exercises ELF program header behavior from binfmt ELF code included in the fs test build context.

Notable invariants and risks:
- Captures regression coverage for a historical linux-fsdevel case involving unordered load segments.

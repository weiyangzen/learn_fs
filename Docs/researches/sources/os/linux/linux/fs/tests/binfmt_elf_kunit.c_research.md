# File Research: sources/os/linux/linux/fs/tests/binfmt_elf_kunit.c

Purpose: KUnit coverage for ELF loader `total_mapping_size()` behavior.

Test coverage:
- Verifies null/empty program header inputs return zero.
- Verifies non-`PT_LOAD` headers do not contribute to mapping size.
- Uses a realistic `/bin/mount` program-header layout and expected mapping size `0xE070`.
- Confirms unordered `PT_LOAD` headers produce the same total mapping size.

Structure:
- Single test case `total_mapping_size_test`.
- KUnit suite name is `KBUILD_MODNAME`.

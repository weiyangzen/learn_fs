# File Research: sources/os/linux/linux/mm/rodata_test.c

## Purpose

`mm/rodata_test.c` is a small boot/runtime functional test for kernel read-only data protection. It validates that `.rodata` remains readable, cannot be modified through a nofault kernel write, and is page-aligned.

## Test Flow

`rodata_test()` performs four checks:

1. Reads `rodata_test_data` and verifies it still equals `TEST_VALUE`.
2. Attempts to write zero to `rodata_test_data` with `copy_to_kernel_nofault()`. Success is a failure because the data should be read-only.
3. Reads the value again to ensure it was not changed.
4. Checks `__start_rodata` and `__end_rodata` for `PAGE_SIZE` alignment.

On failure it logs a specific `pr_err()` and returns. On success it logs that all tests were successful.

## Dependencies

The file uses `linux/rodata_test.h`, `linux/uaccess.h`, `linux/mm.h`, and `asm/sections.h`. The section symbols come from architecture/linker setup.

## Filesystem/MM Relevance

This is MM hardening validation, not filesystem functionality. It verifies kernel mapping permissions that protect read-only sections from accidental or malicious writes.

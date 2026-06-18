# File Research: sources/local-fs/mtd-utils/tests/ubi-tests/helpers.h

## Purpose
Macro and prototype header for UBI tests.

## Key Elements
Defines device node pattern, minimum eraseblock count, page size, wrapper macros for error reporting, initial checks, volume checks, pattern checks/updates, expected-failure checking, and size test values near fractions and boundaries.

## Dependencies
Requires libubi types (`libubi_t`, `ubi_dev_info`, `ubi_mkvol_request`) to be visible to users, plus stdio/string headers.

## Behavior/Risks
Macros assume local variables such as `PROGRAM_NAME`, `libubi`, and `dev_info` exist in the including test file, coupling helpers tightly to the test program structure.

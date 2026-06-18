# sources/security-integrity/selinux/libsepol/cil/test/unit/CilTest.h

## Purpose
`CilTest.h` declares shared fixtures used by CIL unit tests. It keeps helper data and tree-construction APIs available across individual `test_cil_*` modules.

## Important APIs, Types, And Functions
The header defines `struct cil_file_data` with `char *buffer` and `uint32_t file_size`, matching the buffer returned by `set_cil_file_data()`. It declares `set_cil_file_data(struct cil_file_data **)` and `gen_test_tree(struct cil_tree **, char **)`.

## Control Flow
There is no executable flow in the header. Tests include it to call helper functions implemented in `CilTest.c`.

## State And Persistence
The declared `struct cil_file_data` describes in-memory file contents. Ownership rules are not documented in the header; callers need to know that the implementation allocates both the struct and its buffer.

## Dependencies And Integration Points
It includes `../../src/cil_tree.h` for `struct cil_tree`. It integrates with the unit-test helper implementation in `CilTest.c` and any test module needing synthetic parse trees or policy file buffers.

## Risks
The header uses `uint32_t` without directly including `<stdint.h>`, relying on included CIL headers to provide it. The helper prototypes omit parameter names and ownership documentation, increasing the chance of leaks or misuse in tests.

## Test Signals
Use of this header signals tests that need shared CIL tree/file fixtures rather than isolated assertions.

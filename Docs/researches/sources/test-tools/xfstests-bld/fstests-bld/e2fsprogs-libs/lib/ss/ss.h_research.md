# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/ss.h

## Purpose
`ss.h` is the public header for the MIT subsystem command library.

## Important APIs, Types, and Functions
It defines `ss_request_entry`, `ss_request_table`, `ss_rp_options`, flags such as `SS_OPT_DONT_LIST`, and public functions for invocation lifecycle, command execution, table management, prompt management, built-ins, errors, and optional readline.

## Control Flow
There is no runtime control flow. The header establishes command function prototypes through `__SS_PROTO` and printf attributes for `ss_error()`.

## State, Persistence, Dependencies, Risks, and Test Signals
State is exposed through opaque integer invocation IDs and request-table pointers. Dependencies include generated `<ss/ss_err.h>` and compiler attribute support. Risks include ABI compatibility with generated command-table C files and const-correctness tradeoffs from legacy K&R style. Test signals are successful compilation of generated `std_rqs.c`, `test_cmd.c`, and consumers including `test_ss.c`.

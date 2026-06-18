# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_list.h

## Purpose
This header declares CIL list utility unit tests for the CuTest harness.

## Important APIs, Types, And Functions
It includes `CuTest.h` and declares append/prepend test functions and negative cases. It declares `test_cil_list_item_init(CuTest *)`, but the implementation read contains `test_cil_list_init(CuTest *tc)` instead.

## Control Flow
The header itself has no runtime flow. `CilTest.c` registers a subset of list tests; notably it registers append and prepend cases but not the apparent init-name mismatch.

## State And Persistence
No state is stored. It is a compile-time interface for suite registration.

## Dependencies And Integration Points
It integrates with `test_cil_list.c` and `CilTest.c`, and indirectly with the `cil_internal` list utilities.

## Risks
The declaration/implementation mismatch between `test_cil_list_item_init` and `test_cil_list_init` is a drift risk. If someone tries to register the declared init function, linking will fail unless the implementation is renamed or an alias is added. Narrow declarations also omit a direct `test_cil_list_prepend_item` prototype despite the implementation containing that function.

## Test Signals
The header signals intended coverage for append, multiple append, append invalid arguments, prepend, prepend invalid linked item, and prepend null arguments.

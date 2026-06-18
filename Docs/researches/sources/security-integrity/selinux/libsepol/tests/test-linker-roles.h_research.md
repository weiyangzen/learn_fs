<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-linker-roles.h -->
# sources/security-integrity/selinux/libsepol/tests/test-linker-roles.h

## Purpose

Header for the corresponding libsepol CUnit test module. It exposes the test entry point(s) `base_role_tests, module_role_tests` while hiding implementation details in the paired `.c` file. The source was read completely for this report (29 lines).

## Important APIs, Types, and Functions

Contains an include guard and prototypes for `base_role_tests, module_role_tests`. No types or macros beyond the guard are part of the API.

## Control Flow

There is no executable control flow; CUnit harness files include this header to register or invoke the test functions.

## State and Persistence Behavior

No state is declared or stored in this header.

## Dependencies and Integration Points

Integrated with the libsepol tests build and the paired implementation file in the same directory.

## Risks and Edge Cases

The main risk is prototype drift between the header, implementation, and suite registration code.

## Test Signals

Compile/link success of the CUnit test binary is the relevant signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/test-linker-roles.h -->

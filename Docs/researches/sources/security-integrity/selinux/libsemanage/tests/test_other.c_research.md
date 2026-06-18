# sources/security-integrity/selinux/libsemanage/tests/test_other.c

## Purpose
`test_other.c` groups smaller libsemanage tests that do not fit the object-specific suites: SELinux context record manipulation and one debug/error-path check for module priority validation.

## Important APIs, Types, and Functions
`test_semanage_context` exercises `semanage_context_t` with `semanage_context_create`, setters/getters for user, role, type, and MLS, `semanage_context_to_string`, `semanage_context_from_string`, `semanage_context_clone`, and `semanage_context_free`. `test_debug` creates a handle and `semanage_module_info_t`, then verifies that `semanage_module_info_set_priority` rejects a priority cast from `-42` to `uint16_t`.

## Control Flow
`other_test_init` and `other_test_cleanup` are no-ops. `other_add_tests` registers `test_semanage_context` and `test_debug`. The context test uses `setup_handle(SH_CONNECT)`, builds a context, serializes it, parses another context string, clones it, and compares all fields. The debug test constructs its own handle instead of using shared setup, connects, creates module info, exercises the invalid-priority path, then explicitly destroys module info and the handle.

## State and Persistence Behavior
No policy files are created by this suite. The context test uses only heap-allocated context objects plus a libsemanage connection. The debug test allocates a handle and module info object and frees both after the assertion.

## Dependencies and Integration Points
The file depends on CUnit, `utilities.h`, libsemanage context APIs, and module-info APIs. It is registered by the test runner through `other_add_tests`.

## Risks and Edge Cases
`test_debug` calls `semanage_module_info_destroy(sh, modinfo)` and then `free(modinfo)`, which assumes the destroy function only releases internals and not the outer allocation. The priority test is tied to libsemanage's accepted numeric range and unsigned-cast behavior. The context test validates simple four-field MLS contexts but does not cover contexts without MLS or malformed strings.

## Test Signals
Signals include exact field equality for context setters/getters, string serialization to `user_u:role_r:type_t:s0`, parsing and cloning of `my_u:my_r:my_t:s0`, and a negative return from invalid module priority assignment.

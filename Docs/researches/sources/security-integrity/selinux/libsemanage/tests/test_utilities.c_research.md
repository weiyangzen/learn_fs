# sources/security-integrity/selinux/libsemanage/tests/test_utilities.c

## Purpose
`test_utilities.c` is the CUnit suite for helper functions implemented in libsemanage's `src/utilities.c`. It validates string splitting, list helpers, trimming, replacement, config-value lookup, file filtering, and basename handling.

## Important APIs, Types, and Functions
Suite hooks are `semanage_utilities_test_init`, `semanage_utilities_test_cleanup`, and `semanage_utilities_add_tests`. Tested APIs include `semanage_is_prefix`, `semanage_split_on_space`, `semanage_split`, `semanage_list_push`, `semanage_list_pop`, `semanage_list_sort`, `semanage_list_find`, `semanage_list_destroy`, `semanage_str_count`, `semanage_rtrim`, `semanage_str_replace`, `semanage_findval`, `semanage_slurp_file_filter`, and `semanage_basename`.

## Control Flow
Initialization creates a temporary file from the template `TEST_TEMP_XXXXXX`, wraps it in a `FILE *`, writes fixture lines including `sigma=foo` and comment lines, and rewinds. Cleanup unlinks the temp file. `semanage_utilities_add_tests` registers each utility test and cleans up the CUnit registry if registration fails.

Individual tests allocate mutable strings where the API consumes or returns heap memory. The file-filter test supplies a predicate that keeps lines beginning with `#`. The basename test checks ordinary paths, trailing slash behavior, dot, empty string, and root slash.

## State and Persistence Behavior
The suite owns process-global `fd` and `fptr` plus the temporary filename buffer mutated by `mkstemp`. Most tests allocate and free returned strings/lists. The temporary file remains open for the suite duration and is rewound before repeated lookup/filter tests.

## Dependencies and Integration Points
Dependencies include CUnit, the installed/internal `<utilities.h>` for libsemanage utility APIs, standard C/POSIX I/O, and shared test `utilities.h`. It integrates with the broader test binary through the declared suite hooks.

## Risks and Edge Cases
The cleanup unlinks but does not explicitly close `fptr` or `fd`, relying on process teardown or external runner behavior. `test_semanage_split_on_space` and `test_semanage_split` repeatedly free the previous input string and assign the returned remainder, so API ownership assumptions are central. The registration function uses `CU_cleanup_registry` on failure, affecting all suites in the registry.

## Test Signals
Signals include expected prefix truth values, exact split remainders, list length/order/find behavior, character counts, trim output, full and limited string replacement, config lookup values, exactly two filtered comment lines, and basename edge-case outputs.

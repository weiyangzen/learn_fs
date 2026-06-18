<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/test.c -->
# sources/security-integrity/ecryptfs-utils/src/utils/test.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/test.c_research.md`. Source lines read for this pass: 481.

## Purpose
Non-installed C test harness for legacy eCryptfs extent translation, lower-size calculations, simulated page encryption flow, and parsing of `ecryptfsrc` options.

## Important APIs, Types, And Functions
Defines local test structs plus `ecryptfs_extent_to_lwr_pg_idx_and_offset`, `test_extent_translation`, simulated lower-page helpers, `ecryptfs_encrypt_page`, `upper_size_to_lower_size`, `test_upper_size_to_lower_size`, `test_nv_list_from_file`, and `main`.

## Control Flow
Current `main` runs only `test_nv_list_from_file` and jumps to exit, so later extent/encrypt/size tests are unreachable without editing. The simulated encryption path traces lower-page reads/writes rather than performing real crypto.

## State And Persistence Behavior
Reads local `ecryptfsrc`; otherwise allocates/free simulated page state and prints diagnostics.

## Dependencies And Integration Points
Depends on libecryptfs parser `parse_options_file`, C stdlib, and local `io.c` linkage in Makefile.

## Risks And Edge Cases
Because most tests are unreachable, build success does not imply extent translation coverage. This is a developer harness rather than a reliable regression suite.

## Test Signals
To make it useful, remove the early `goto out` or split the option parser test from the extent/size vector tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/test.c -->

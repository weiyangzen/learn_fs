<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/gen_key.c -->
# sources/security-integrity/ecryptfs-utils/src/utils/gen_key.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/gen_key.c_research.md`. Source lines read for this pass: 181.

## Purpose
Legacy helper code for public/private key generation directory setup; the main key generation routine is currently stubbed out.

## Important APIs, Types, And Functions
Defines `ecryptfs_generate_key` returning `-EINVAL`, plus `create_subdirectory` and `create_default_dir` for `~/.ecryptfs/pki/<module>` paths.

## Control Flow
The disabled block shows intended decision-graph/key-module selection. Active code only creates default PKI directories and subdirectories from slash-separated relative file paths.

## State And Persistence Behavior
Can create `~/.ecryptfs`, `~/.ecryptfs/pki`, and `~/.ecryptfs/pki/<alias>` with mode 0700 via helper calls.

## Dependencies And Integration Points
Depends on `struct ecryptfs_key_mod`, passwd/home information from callers, mkdir, and eCryptfs headers.

## Risks And Edge Cases
`create_subdirectory` mutates the input string in place while walking slashes and has limited cleanup on allocation errors. The exported generate function is nonfunctional.

## Test Signals
Directory creation helpers should be tested with nested relative names, existing directories, and invalid permissions. `ecryptfs_generate_key` should currently be expected to fail.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/gen_key.c -->

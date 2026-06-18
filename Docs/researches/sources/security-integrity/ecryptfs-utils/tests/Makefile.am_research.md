<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/Makefile.am -->
# sources/security-integrity/ecryptfs-utils/tests/Makefile.am

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/Makefile.am_research.md`. Source lines read for this pass: 3.

## Purpose
Top-level Automake manifest for the eCryptfs test hierarchy.

## Important APIs, Types, And Functions
Declares `SUBDIRS = lib userspace kernel`, distributes `run_tests.sh`, `new.sh`, and `tests.rc`.

## Control Flow
Automake recurses into library, userspace, and kernel test directories during build/test setup.

## State And Persistence Behavior
No runtime persistence; controls build-system traversal and distributed test metadata.

## Dependencies And Integration Points
Depends on autotools and the subordinate test directories.

## Risks And Edge Cases
Removing a subdirectory here silently drops an entire test lane from recursive builds.

## Test Signals
A recursive `make check` or distribution tarball validation should include the listed subdirectories and scripts.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/Makefile.am -->

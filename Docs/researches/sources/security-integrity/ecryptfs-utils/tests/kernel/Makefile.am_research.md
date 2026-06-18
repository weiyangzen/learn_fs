<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/Makefile.am -->
# sources/security-integrity/ecryptfs-utils/tests/kernel/Makefile.am

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/tests/kernel/Makefile.am_research.md`. Source lines read for this pass: 92.

## Purpose
Automake manifest for kernel-level eCryptfs regression scripts and compiled fixtures.

## Important APIs, Types, And Functions
Lists distributed shell tests in `dist_noinst_SCRIPTS`, compiled fixtures in `noinst_PROGRAMS` under `ENABLE_TESTS`, per-fixture `_SOURCES`, and one libecryptfs-linked miscdev test.

## Control Flow
Builds C fixtures only when tests are enabled and packages the shell wrappers that orchestrate eCryptfs lower/upper mounts.

## State And Persistence Behavior
No runtime state; controls which regression tests are available to the test runner.

## Dependencies And Integration Points
Depends on autotools, C compiler, eCryptfs test helper library, and libecryptfs for miscdev-bad-count.

## Risks And Edge Cases
A missing source mapping means the wrapper may exist without its binary. The manifest also includes tests outside this work item, so edits can affect broader coverage.

## Test Signals
`make check ENABLE_TESTS` should compile all `noinst_PROGRAMS` and make wrappers available.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/tests/kernel/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/tests/Makefile -->
# sources/security-integrity/keyutils/tests/Makefile

## Purpose

`tests/Makefile` is the RHTS-style test harness entry point for the keyutils testsuite. It discovers all `runtest.sh` files and runs them through the top-level test runner.

## Important APIs, Types, and Functions

Variables define namespace/package metadata, `TESTVERSION`, `TEST`, discovered `TESTS`, `FILES`, and optional `METADATA` generation when Red Hat test harness includes are available. Targets include `run`, `build`, and `clean`.

## Control Flow

`run` depends on files/build and invokes `bash runtest.sh $(TESTS)`. `TESTS` is produced with `find` and path cleanup. `clean` removes temporary files and nested `test.out` artifacts. Under `/usr/share/rhts/lib/rhts-make.include`, metadata is generated and linted.

## State and Persistence Behavior

The Makefile writes test metadata only in RHTS environments and deletes `test.out` files on clean. Test scripts themselves mutate kernel keyrings during execution.

## Dependencies and Integration Points

It depends on bash, find, sed, optional RHTS make include/lint tooling, and the sibling `runtest.sh` orchestrator plus all nested test directories.

## Risks and Edge Cases

Discovery includes every nested `runtest.sh`, so newly added tests run automatically. Environment-specific RHTS metadata generation can fail if support tools are partially installed. Clean uses `find *`, so it assumes a populated tests directory.

## Test Signals

`make run` should invoke the full test list, and `make clean` should remove transient outputs without deleting test sources.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/tests/Makefile -->

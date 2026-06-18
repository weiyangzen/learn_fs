# sources/security-integrity/selinux/libsemanage/tests/Makefile

## Purpose
Builds and runs the libsemanage CUnit test binary and compiles test CIL policies.

## Targets and dependencies
`SOURCES` and `CILS` are wildcard-driven. `all` builds `libsemanage-tests` and `.policy` outputs from `.cil` inputs via `../../secilc/secilc`. The test executable links every object with `../src/libsemanage.a` and `-lcunit -lbz2 -laudit -lselinux -lsepol`. `test` runs the binary.

## Risks and test signals
Wildcard ordering is sorted for determinism. Tests depend on local secilc, static libsemanage, and system SELinux/audit/sepol libraries. No parallel-test isolation is defined in this Makefile.

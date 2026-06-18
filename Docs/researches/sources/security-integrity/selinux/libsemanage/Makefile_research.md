<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/Makefile -->
# sources/security-integrity/selinux/libsemanage/Makefile

## Purpose
Top-level dispatcher Makefile for libsemanage build, wrapper generation, install, relabel, clean, and tests.

## Important APIs, Types, And Functions
Targets delegate to subdirectories: `src` for `all`, `swigify`, `pywrap`, `rubywrap`, relabel, and wrapper installs; `include`, `man`, and `utils` for install; `tests` for clean/distclean and `test`.

## Control Flow
Each rule is a simple recursive `$(MAKE) -C <dir> <target>` call, preserving the caller's make variables.

## State And Persistence Behavior
Build/install/test state is produced by delegated sub-makes. This file itself creates no artifacts directly.

## Dependencies And Integration Points
Coordinates libsemanage subprojects and provides stable top-level targets for packaging/build systems.

## Risks And Test Signals
Risks include recursive make target drift, missing subdirectories, and install target ordering. Test signals are top-level `make all`, `make test`, wrapper targets, staged install, and clean/distclean delegation.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsemanage/Makefile -->

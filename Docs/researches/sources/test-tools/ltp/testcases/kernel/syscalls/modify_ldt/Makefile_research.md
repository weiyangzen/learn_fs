<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/modify_ldt/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/modify_ldt/Makefile

## Purpose
This file builds the modify_ldt leaf tests through the common LTP make infrastructure.

## Important APIs, Types, and Functions
This is an LTP leaf Makefile. It sets `top_srcdir`, includes `include/mk/testcases.mk`, and finishes with `include/mk/generic_leaf_target.mk`.
There are no local compiler or linker overrides beyond the common LTP leaf rules.

## Control Flow
Build control flows through the common LTP make includes: test discovery/compilation is provided by `testcases.mk`, while `generic_leaf_target.mk` supplies the default all/install/clean behavior. Any assignments above those includes affect every target in this syscall directory or, for target-specific lines, the named binary only.

## State and Persistence
Persistent or externally visible state includes build variables only; no runtime persistence. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `modify_ldt` syscall test directory. x86/i386 LDT ABI via lapi/ldt.h and SAFE_MODIFY_LDT; tests are architecture-gated.

## Risks
Risks: incorrect local linker/compiler flags would cause build-only failures for all tests in this directory.

## Test Signals
successful compilation/linking of directory targets is the observable signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/modify_ldt/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mount/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mount/Makefile

## Purpose
This file builds mount syscall tests with _GNU_SOURCE enabled for GNU mount-related interfaces.

## Important APIs, Types, and Functions
This is an LTP leaf Makefile. It sets `top_srcdir`, includes `include/mk/testcases.mk`, and finishes with `include/mk/generic_leaf_target.mk`.
Local build customizations: `CFLAGS			+= -D_GNU_SOURCE`.

## Control Flow
Build control flows through the common LTP make includes: test discovery/compilation is provided by `testcases.mk`, while `generic_leaf_target.mk` supplies the default all/install/clean behavior. Any assignments above those includes affect every target in this syscall directory or, for target-specific lines, the named binary only.

## State and Persistence
Persistent or externally visible state includes build variables only; no runtime persistence. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mount` syscall test directory. LTP device formatting/mountpoint support, root privileges, filesystem skip lists, statfs/statvfs, and helper resource files.

## Risks
Risks: incorrect local linker/compiler flags would cause build-only failures for all tests in this directory.

## Test Signals
successful compilation/linking of directory targets is the observable signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mount/Makefile -->

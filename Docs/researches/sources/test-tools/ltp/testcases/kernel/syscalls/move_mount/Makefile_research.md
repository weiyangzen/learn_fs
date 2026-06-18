<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_mount/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/move_mount/Makefile

## Purpose
This file builds move_mount tests through generic LTP syscall test rules.

## Important APIs, Types, and Functions
This is an LTP leaf Makefile. It sets `top_srcdir`, includes `include/mk/testcases.mk`, and finishes with `include/mk/generic_leaf_target.mk`.
There are no local compiler or linker overrides beyond the common LTP leaf rules.

## Control Flow
Build control flows through the common LTP make includes: test discovery/compilation is provided by `testcases.mk`, while `generic_leaf_target.mk` supplies the default all/install/clean behavior. Any assignments above those includes affect every target in this syscall directory or, for target-specific lines, the named binary only.

## State and Persistence
Persistent or externally visible state includes build variables only; no runtime persistence. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `move_mount` syscall test directory. new mount API wrappers fsopen/fsconfig/fsmount/open_tree/move_mount, root privileges, formatted devices, tmpfs, and kernel-version gates.

## Risks
Risks: incorrect local linker/compiler flags would cause build-only failures for all tests in this directory.

## Test Signals
successful compilation/linking of directory targets is the observable signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_mount/Makefile -->

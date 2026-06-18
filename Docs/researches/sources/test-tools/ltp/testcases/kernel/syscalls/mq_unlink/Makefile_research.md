<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mq_unlink/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mq_unlink/Makefile

## Purpose
This file builds mq_unlink tests with pthread and realtime library linkage.

## Important APIs, Types, and Functions
This is an LTP leaf Makefile. It sets `top_srcdir`, includes `include/mk/testcases.mk`, and finishes with `include/mk/generic_leaf_target.mk`.
Local build customizations: `LDLIBS			+= -lpthread -lrt`.

## Control Flow
Build control flows through the common LTP make includes: test discovery/compilation is provided by `testcases.mk`, while `generic_leaf_target.mk` supplies the default all/install/clean behavior. Any assignments above those includes affect every target in this syscall directory or, for target-specific lines, the named binary only.

## State and Persistence
Persistent or externally visible state includes child/thread synchronization and signal-observed outcomes. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mq_unlink` syscall test directory. POSIX message queues, root/nobody credentials, long queue-name boundary cases, and mqueue cleanup.

## Risks
Risks: signal or child-process expectations can be timing-sensitive; incorrect local linker/compiler flags would cause build-only failures for all tests in this directory.

## Test Signals
successful compilation/linking of directory targets is the observable signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mq_unlink/Makefile -->

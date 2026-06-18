<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mq_timedreceive/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mq_timedreceive/Makefile

## Purpose
This file builds mq_timedreceive tests with POSIX IPC helper include path and pthread/rt libraries.

## Important APIs, Types, and Functions
This is an LTP leaf Makefile. It sets `top_srcdir`, includes `include/mk/testcases.mk`, and finishes with `include/mk/generic_leaf_target.mk`.
Local build customizations: `CPPFLAGS		+= -I$(abs_srcdir)/../utils`; `LDLIBS			+= -lpthread -lrt`.

## Control Flow
Build control flows through the common LTP make includes: test discovery/compilation is provided by `testcases.mk`, while `generic_leaf_target.mk` supplies the default all/install/clean behavior. Any assignments above those includes affect every target in this syscall directory or, for target-specific lines, the named binary only.

## State and Persistence
Persistent or externally visible state includes child/thread synchronization and signal-observed outcomes. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mq_timedreceive` syscall test directory. shared mq_timed helper variants for libc/time64 syscalls, POSIX queues, signals, timeouts, and child isolation for bad pointers.

## Risks
Risks: signal or child-process expectations can be timing-sensitive; incorrect local linker/compiler flags would cause build-only failures for all tests in this directory.

## Test Signals
successful compilation/linking of directory targets is the observable signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mq_timedreceive/Makefile -->

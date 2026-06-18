<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/Makefile

## Purpose
This file builds move_pages numbered tests, links each with move_pages_support.o, and adds pthread/rt plus NUMA utility include paths.

## Important APIs, Types, and Functions
This is an LTP leaf Makefile. It sets `top_srcdir`, includes `include/mk/testcases.mk`, and finishes with `include/mk/generic_leaf_target.mk`.
Local build customizations: `CPPFLAGS		+= -I$(abs_srcdir)/../utils`; `MAKE_TARGETS		:= $(patsubst $(abs_srcdir)/%.c,%,$(sort $(wildcard $(abs_srcdir)/*[0-9].c)))`; `LDLIBS			+= -lpthread -lrt`.

## Control Flow
Build control flows through the common LTP make includes: test discovery/compilation is provided by `testcases.mk`, while `generic_leaf_target.mk` supplies the default all/install/clean behavior. Any assignments above those includes affect every target in this syscall directory or, for target-specific lines, the named binary only.

## State and Persistence
Persistent or externally visible state includes NUMA placement, page migration status, or hugepage sysfs settings; child/thread synchronization and signal-observed outcomes. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `move_pages` syscall test directory. libnuma/numaif, LTP NUMA helpers, allowed memory node discovery, root or nobody credentials for permission tests, and shared semaphore synchronization.

## Risks
Risks: signal or child-process expectations can be timing-sensitive; incorrect local linker/compiler flags would cause build-only failures for all tests in this directory.

## Test Signals
successful compilation/linking of directory targets is the observable signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/Makefile -->

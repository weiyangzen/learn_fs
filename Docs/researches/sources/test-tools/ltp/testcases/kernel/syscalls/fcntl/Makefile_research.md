# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/Makefile

Purpose: builds the `fcntl` syscall test suite with additional libraries, large-file variants, and GNU/largefile feature defines.

Important APIs/types/functions: per-target `LDLIBS` additions for `fcntl33`, `fcntl34`, and `fcntl36`, include `testcases.mk`, include `../utils/newer_64.mk`, pattern rule `%_64: CPPFLAGS += -D_FILE_OFFSET_BITS=64`, global `CPPFLAGS += -D_GNU_SOURCE -D_LARGEFILE64_SOURCE`, and `generic_leaf_target.mk`.

Control flow: target-specific library flags are declared first, then common rules and 64-bit variant support are loaded, then compile flags and generic targets are applied.

State/persistence behavior: no runtime state. Build state includes extra 64-bit test binaries and linked realtime/pthread dependencies for selected tests.

Dependencies/integration: integrates legacy and modern fcntl tests with LTP large-file build infrastructure.

Risks/test signals: incorrect flags could hide GNU constants or large-file APIs. Build failures are the primary signal.

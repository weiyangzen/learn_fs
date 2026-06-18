<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utils/newer_64.mk -->
# sources/test-tools/ltp/testcases/kernel/syscalls/utils/newer_64.mk

Purpose: LTP make fragment that builds normal syscall tests and optional `_64` variants for syscalls with newer 64-bit interfaces. It mirrors the older compat make pattern while adding a `TST_USE_NEWER64_SYSCALL` preprocessor flag for generated suffixed targets.

Important APIs/types/functions: appends include paths for the source dir and `../utils`, discovers `SRCS` from `*.c`, builds `MAKE_TARGETS` from source basenames, and conditionally adds `_64` targets unless `TST_NEWER_64_SYSCALL=no`. `DEF_64` is `TST_USE_NEWER64_SYSCALL`; `%_64` adds `-D$(DEF_64)=1`, and `%_64.o: %.c` compiles the same source under the suffixed object name.

Control flow/state: make-time logic checks for `../utils/newer_64.h` and sets `HAS_NEWER_64`, but the comments note this block is questionable because not all users have the matching header/define. No runtime state exists.

Dependencies/integration: consumed by syscall test directories that need paired native/newer-64 builds. It depends on LTP's common pattern rules and source-tree variables such as `abs_srcdir` and `COMPILE.c`.

Risks/test signals: the fragment can silently create extra targets that fail if source code does not honor `TST_USE_NEWER64_SYSCALL`. Build logs for unexpected `_64` target failures are the primary signal; setting `TST_NEWER_64_SYSCALL=no` suppresses the variant path.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utils/newer_64.mk -->

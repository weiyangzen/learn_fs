<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_loop-nv.c -->
# sources/test-tools/strace/tests/ioctl_loop-nv.c

Purpose: abbreviated non-verbose loop-device ioctl variant. It defines `ABBREV 1` before including `ioctl_loop.c`, forcing complex loop structs to print as pointers.

Important APIs/types/functions: Inherits loop ioctls and types from `ioctl_loop.c`: `loop_info`, `loop_info64`, `loop_config`, `LOOP_*`, `LO_FLAGS_*`, and `LO_CRYPT_*`. Local behavior is controlled by `ABBREV`.

Control flow: runtime follows the base test's unknown command, `LOOP_SET_FD`, info, status64, configure, block-size, direct-io, and control ioctl coverage, but `print_loop_info*` and `print_loop_config` choose pointer output.

State and persistence behavior: process-local structs only; invalid fd prevents loop device mutation.

Dependencies/integration points: exercises strace `-X abbrev`-like expected output for loop structs.

Risks and test signals: passing output confirms abbreviation mode suppresses struct expansion while still naming loop ioctl commands correctly.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_loop-nv.c -->

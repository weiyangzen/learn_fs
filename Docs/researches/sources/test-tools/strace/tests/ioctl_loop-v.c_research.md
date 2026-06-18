<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_loop-v.c -->
# sources/test-tools/strace/tests/ioctl_loop-v.c

Purpose: verbose loop-device ioctl variant. It defines `VERBOSE 1` before including `ioctl_loop.c`, enabling full legacy and 64-bit loop struct field printing.

Important APIs/types/functions: Inherits `print_loop_info`, `print_loop_info64`, `print_loop_config`, `struct loop_info`, `loop_info64`, `loop_config`, and `LOOP_*` commands from the base file.

Control flow: same ioctl sequence as `ioctl_loop.c`; verbose branches add device/inode/rdevice, crypt name/key, init arrays, reserved fields, and full 64-bit info fields.

State and persistence behavior: invalid fd and local structs only. Verbose mode changes expected text, not runtime side effects.

Dependencies/integration points: validates strace verbose output for loop ioctls and `makedev` formatting.

Risks and test signals: sensitive to struct layout and word-size formatting. Passing output confirms verbose decoder coverage for loop status/configuration structs.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_loop-v.c -->

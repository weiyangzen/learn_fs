<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_loop.c -->
# sources/test-tools/strace/tests/ioctl_loop.c

Purpose: tests decoding of loop device ioctl commands, including legacy `loop_info`, modern `loop_info64`, `loop_config`, control commands, unknown commands, flags, encryption fields, and file descriptor/scalar arguments.

Important APIs/types/functions: Uses raw `sys_ioctl`, `print_loop_info`, `print_loop_info64`, `print_loop_config`, `linux/loop.h`, `print_fields.h`, `major/minor`, `struct loop_info`, `loop_info64`, `loop_config`, `LOOP_SET_FD`, `LOOP_GET_STATUS`, `LOOP_SET_STATUS64`, `LOOP_CONFIGURE`, `LOOP_CTL_*`, and xlat strings for flags/encryption.

Control flow: `main` allocates loop structs, prints unknown loop command decoding, tests scalar commands such as `LOOP_SET_FD`, fills legacy and 64-bit info structs with crafted names, offsets, flags, encryption values, and reserved fields, then checks get/set status variants, clear fd, block size, direct IO, configure, and loop-control commands.

State and persistence behavior: no real loop device is touched because fd is `-1`; all values come from stack/tail-allocated test structs. Macro modes `ABBREV` and `VERBOSE` alter field expansion.

Dependencies/integration points: depends on Linux loop UAPI, strace xlat tables, `scno.h`, and helper macros. Integrates with output modes for pointer abbreviation, verbose field printing, and ioctl-number fallback.

Risks and test signals: loop UAPI grows over time, so reserved/unknown decoding is fragile. Passing output confirms command recognition, flag/encryption xlat behavior, struct string truncation, 32/64-bit field formatting, and `loop_config` nested decoding.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_loop.c -->

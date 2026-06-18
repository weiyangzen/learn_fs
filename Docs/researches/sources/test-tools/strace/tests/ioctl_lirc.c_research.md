<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_lirc.c -->
# sources/test-tools/strace/tests/ioctl_lirc.c

Purpose: tests decoding of Linux infrared remote control (`LIRC_*`) ioctls, covering set commands, mode enums, feature flags, timeout queries, and unknown commands.

Important APIs/types/functions: Uses `do_ioctl`, `linux/lirc.h`, `LIRC_SET_*`, `LIRC_GET_*`, `LIRC_MODE_*`, `LIRC_CAN_*`, and an allocated `unsigned int` argument. Under `INJECT_RETVAL`, it verifies injected success before dereferencing read buffers.

Control flow: optional injection lock loop scans `LIRC_GET_FEATURES`. The main path fills one integer buffer with representative values and calls each set ioctl, printing decoded scalar or xlat values. In injected mode it also calls read ioctls with crafted feature/mode/timeout values and a deliberately shifted pointer. It finishes with an unknown `_IO('i', 0xff)` command.

State and persistence behavior: no device state changes because fd is `-1`; all state is one test integer and injected-return bookkeeping.

Dependencies/integration points: depends on `linux/lirc.h`, strace xlat tables for LIRC modes/features, syscall injection, and `sprintrc`.

Risks and test signals: kernel header aliases can make output mention another command (`IPMICTL_SET_MAINTENANCE_MODE_CMD`, `I2OVALIDATE`). Passing output confirms set/read direction classification, enum/flag formatting, unknown command fallback, and injected-success buffer decoding.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_lirc.c -->

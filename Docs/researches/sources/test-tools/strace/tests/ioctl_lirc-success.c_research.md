<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_lirc-success.c -->
# sources/test-tools/strace/tests/ioctl_lirc-success.c

Purpose: syscall-injection success variant for LIRC ioctl decoding. It defines `INJECT_RETVAL 42` and includes the base LIRC test so read-style ioctls are decoded as if the kernel returned success.

Important APIs/types/functions: Inherits `do_ioctl`, LIRC command constants, and unsigned-int argument decoding from `ioctl_lirc.c`. The only local API is the `INJECT_RETVAL` macro.

Control flow: the included `main` first consumes a `NUM_SKIP` argument and loops on `LIRC_GET_FEATURES` until the injected return appears. Then it runs the normal LIRC command matrix with success-only sections enabled for get operations.

State and persistence behavior: process-local integer buffer only. Injection affects expected `sprintrc` text and lets strace print dereferenced output buffers.

Dependencies/integration points: integrates strace syscall injection harness with `linux/lirc.h` xlat decoding.

Risks and test signals: requires the runner to pass the correct injection skip count. Passing output confirms successful LIRC get-ioctl value and flag decoding under injected return values.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_lirc-success.c -->

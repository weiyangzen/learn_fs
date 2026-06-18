<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_mtd-success.c -->
# sources/test-tools/strace/tests/ioctl_mtd-success.c

Purpose: injected-success variant for MTD ioctl decoding. It defines `INJECT_RETVAL 42` and includes `ioctl_mtd.c`.

Important APIs/types/functions: Inherits all MTD helpers and UAPI structs from the base file; local effect is enabling success-return branches and injected `sprintrc` text.

Control flow: included `main` locks onto an injected MTD ioctl return, then executes the base MTD command matrix with read-style structs printed as successful outputs instead of pointers.

State and persistence behavior: local tail-allocated MTD structs only; injection simulates kernel writes without a device.

Dependencies/integration points: integrates strace injection with `mtd/mtd-abi.h` decoder coverage.

Risks and test signals: requires correct injection arguments. Passing output confirms successful MTD struct decoding paths, not just EBADF pointer fallback.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_mtd-success.c -->

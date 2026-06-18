<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp-success.c -->
# sources/test-tools/strace/tests/ioctl_seccomp-success.c

Purpose: injected-success variant for seccomp user notification ioctl decoding. It defines `INJECT_RETVAL 1` and includes the base seccomp test.

Important APIs/types/functions: Inherits all seccomp notification structs and command coverage from `ioctl_seccomp.c`; injection changes `INJ_STR` and success branches.

Control flow: included `main` can early-exit without injection args; otherwise it locks onto injected `SECCOMP_IOCTL_NOTIF_RECV`, then executes unknown command, receive/send/id-valid/addfd/set-flags cases as success-return output.

State and persistence behavior: local structs and two controlled fds for `/dev/null` and `/dev/zero`; injection simulates successful notification operations.

Dependencies/integration points: validates strace injection for seccomp ioctl decoders.

Risks and test signals: injection retval is `1`, not `42`, so harness configuration matters. Passing output confirms success-path struct before/after rendering for seccomp notifications.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp-success.c -->

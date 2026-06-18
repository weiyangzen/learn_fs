<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp-y-success-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_seccomp-y-success-Xabbrev.c

Purpose: fd-path plus injected-success seccomp variant with abbreviated xlat output.

Important APIs/types/functions: Defines `XLAT_ABBREV 1` and includes `ioctl_seccomp-y-success.c`, inheriting seccomp user notification structs and commands.

Control flow: base seccomp test runs in success mode with fd path annotations and abbreviated xlat command/flag strings.

State and persistence behavior: local structs and controlled fds only.

Dependencies/integration points: validates `-y`, injection, and `-X abbrev` together.

Risks and test signals: sensitive to both fd path availability and xlat wording. Passing output confirms option composition.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp-y-success-Xabbrev.c -->

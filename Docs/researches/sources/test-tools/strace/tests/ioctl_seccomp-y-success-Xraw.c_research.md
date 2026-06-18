<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp-y-success-Xraw.c -->
# sources/test-tools/strace/tests/ioctl_seccomp-y-success-Xraw.c

Purpose: fd-path plus injected-success seccomp variant with raw xlat output.

Important APIs/types/functions: Defines `XLAT_RAW 1` and includes `ioctl_seccomp-y-success.c`.

Control flow: runs the seccomp success matrix with raw numeric command/flag output while printing fd paths for addfd source descriptors.

State and persistence behavior: local structs and controlled fds only.

Dependencies/integration points: validates `-y`, injection, and `-X raw` composition.

Risks and test signals: numeric command encodings are header-sensitive. Passing output confirms raw mode and fd-path annotations both work.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp-y-success-Xraw.c -->

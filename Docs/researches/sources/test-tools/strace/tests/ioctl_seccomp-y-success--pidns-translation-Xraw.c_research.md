<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp-y-success--pidns-translation-Xraw.c -->
# sources/test-tools/strace/tests/ioctl_seccomp-y-success--pidns-translation-Xraw.c

Purpose: combined seccomp variant for fd paths, injected success, pidns translation, and raw xlat output.

Important APIs/types/functions: Defines `XLAT_RAW 1` and includes the `-y` success pidns wrapper, inheriting seccomp notification commands and structs.

Control flow: executes the base seccomp matrix with injected success and raw numeric command/flag values while preserving fd path and pid translation decorations.

State and persistence behavior: local structs and controlled fds only.

Dependencies/integration points: validates composition of `-X raw`, `-y`, pidns translation, and syscall injection.

Risks and test signals: raw numeric encodings must match headers. Passing output confirms raw mode does not break fd-path or pidns annotations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp-y-success--pidns-translation-Xraw.c -->

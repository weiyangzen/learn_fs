<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp-y-success--pidns-translation-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_seccomp-y-success--pidns-translation-Xverbose.c

Purpose: combined seccomp variant for fd paths, injected success, pidns translation, and verbose xlat output.

Important APIs/types/functions: Defines `XLAT_VERBOSE 1` and includes the layered `ioctl_seccomp-y-success--pidns-translation.c` wrapper.

Control flow: base seccomp notification tests run with injected success, path-annotated fds, translated PIDs, and verbose command/flag xlat formatting.

State and persistence behavior: local notification/addfd structs and `/dev/null`/`/dev/zero` fds only.

Dependencies/integration points: validates combined strace option behavior for seccomp ioctls.

Risks and test signals: output is highly formatting-sensitive. Passing output confirms verbose xlat coexists with fd-path and pidns decorations.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp-y-success--pidns-translation-Xverbose.c -->

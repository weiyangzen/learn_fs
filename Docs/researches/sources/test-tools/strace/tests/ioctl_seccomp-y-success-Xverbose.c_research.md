<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp-y-success-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_seccomp-y-success-Xverbose.c

Purpose: fd-path plus injected-success seccomp variant with verbose xlat output.

Important APIs/types/functions: Defines `XLAT_VERBOSE 1` and includes `ioctl_seccomp-y-success.c`.

Control flow: executes the base seccomp notification matrix in injected success mode, printing fd paths and verbose xlat strings.

State and persistence behavior: local notification/addfd structs plus opened `/dev/null` and `/dev/zero` descriptors.

Dependencies/integration points: validates `-y`, injection, and `-X verbose` output composition.

Risks and test signals: exact output is formatting-sensitive. Passing output confirms verbose xlat does not interfere with path-annotated fd fields.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_seccomp-y-success-Xverbose.c -->

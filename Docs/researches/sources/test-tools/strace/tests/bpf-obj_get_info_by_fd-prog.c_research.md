<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/bpf-obj_get_info_by_fd-prog.c -->
## sources/test-tools/strace/tests/bpf-obj_get_info_by_fd-prog.c

Purpose: Program-info variant of the `BPF_OBJ_GET_INFO_BY_FD` test without verbose field expansion.

Important APIs/types/functions: Defines `CHECK_OBJ_PROG 1` and includes `bpf-obj_get_info_by_fd.c`.

Control flow: Enables test BPF program loading and program info queries; non-verbose mode prints info pointers rather than detailed structures.

State and persistence: Creates BPF maps/programs in the included body, serialized by `lock_file_by_dirname`.

Dependencies and integration: Exercises program-info path while keeping expected output less kernel-field-specific.

Risks: BPF program load may fail under unprivileged or locked-down kernels, causing skip.

Test signals: Output should show successful map/program creation attempts and `BPF_OBJ_GET_INFO_BY_FD` program query lines with pointer-style info.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/bpf-obj_get_info_by_fd-prog.c -->

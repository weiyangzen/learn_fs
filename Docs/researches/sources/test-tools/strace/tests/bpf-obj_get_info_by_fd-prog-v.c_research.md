<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/bpf-obj_get_info_by_fd-prog-v.c -->
## sources/test-tools/strace/tests/bpf-obj_get_info_by_fd-prog-v.c

Purpose: Verbose program-info variant of the `BPF_OBJ_GET_INFO_BY_FD` BPF test.

Important APIs/types/functions: Defines `CHECK_OBJ_PROG 1`, `VERBOSE 1`, and includes `bpf-obj_get_info_by_fd.c`.

Control flow: Enables creation/loading of a test BPF program and verbose printing of returned `bpf_prog_info` and map info structures.

State and persistence: Inherited test creates BPF maps/programs and holds fds until process exit; lock file serialization prevents memlock pressure across runs.

Dependencies and integration: Linked with clock libs by `Makefile.am`; depends on BPF syscall support and verbose xlat tables.

Risks: Requires sufficient BPF permissions/kernel support; otherwise the common body skips. Verbose output is sensitive to kernel struct growth.

Test signals: Expected output includes map creation, program load, map info, program info, xlated/map id buffer cases, and verbose symbolic fields.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/bpf-obj_get_info_by_fd-prog-v.c -->

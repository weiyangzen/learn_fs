<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/bpf-obj_get_info_by_fd.c -->
## sources/test-tools/strace/tests/bpf-obj_get_info_by_fd.c

Purpose: Integration-style BPF decoder test for `BPF_OBJ_GET_INFO_BY_FD`, covering real map info and optionally real program info returned by the kernel.

Important APIs/types/functions: Defines `sys_bpf`, `print_map_create`, optional `socket_prog`, `print_prog_load`, `try_bpf`, and `main`. Uses `BPF_MAP_CREATE_struct`, `BPF_PROG_LOAD_struct`, `BPF_OBJ_GET_INFO_BY_FD_struct`, `bpf_map_info_struct`, `bpf_prog_info_struct`, `print_fields.h`, xlat tables, `lock_file_by_dirname`, `tail_alloc`, `clock_gettime`, and `print_time_t_nsec`.

Control flow: Serializes invocations and sleeps for BPF locked-memory reclamation, tries multiple attr sizes to create two array maps, optionally loads a socket filter program referencing those maps, queries map info into exact and oversized buffers, and in program mode queries program info through several caller-provided buffer configurations for xlated instructions and map id arrays. Verbose mode prints decoded returned structs; non-verbose mode prints pointers.

State and persistence: Creates kernel BPF map/program objects and file descriptors for process lifetime. Uses a lock under the test directory to serialize runs and avoid transient memlock failures.

Dependencies and integration: Wrapper files enable program and verbose modes. Requires Linux BPF syscall/header support, anonymous inode fd path decoding, clock APIs for load-time rendering, and xlat tables for map/prog flags/types.

Risks: Highly kernel- and privilege-sensitive; unprivileged BPF restrictions, memlock limits, old kernels, or struct field changes can alter skips/output. Time conversion for program load time is explicitly approximate.

Test signals: Passing output shows map creation attempts, info_len shrink/expansion behavior, fd annotation as `anon_inode:bpf-map`/`bpf-prog`, verbose map/prog fields, map id array truncation cases, and clean exit.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/bpf-obj_get_info_by_fd.c -->

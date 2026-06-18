<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/include/liburing/io_uring/bpf_filter.h -->
## sources/test-tools/liburing/src/include/liburing/io_uring/bpf_filter.h

Purpose: defines the UAPI argument shapes for registering io_uring BPF filters. Filters can inspect request context and allow or deny operations based on opcode and operation-specific packed data.

Important APIs/types/functions: `io_uring_bpf_ctx` carries `user_data`, opcode, SQE flags, auxiliary data size, and per-op unions for socket and open fields. `io_uring_bpf_filter` describes one opcode filter with flags, BPF instruction length, expected PDU size, and pointer to the filter program. `io_uring_bpf` groups filters under a ring fd and task-filter flags. Flags include `IO_URING_BPF_FILTER_DENY_REST`, `IO_URING_BPF_FILTER_SZ_STRICT`, and `IO_URING_BPF_TASK`.

Control flow: not executable by itself. `register.c` passes `io_uring_bpf` to `IORING_REGISTER_BPF_FILTER`, either against a ring or task-wide with fd `-1`.

State and persistence behavior: registered filters persist in kernel state according to the registration target. The header reserves fields for future UAPI extension.

Dependencies and integration points: included by `liburing.h` and `register.c`. Depends on Linux fixed-width types and BPF filter program memory supplied by userspace.

Risks: user and kernel must agree on `pdu_size` for strict registrations. Bad filter pointers or lengths are kernel-facing inputs; liburing only wraps the syscall and does not validate program semantics.

Test signals: not directly covered by the listed tests, but Makefile includes broader BPF-related tests in the suite. Registration failure paths would show through `io_uring_register_bpf_filter*` callers.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/include/liburing/io_uring/bpf_filter.h -->

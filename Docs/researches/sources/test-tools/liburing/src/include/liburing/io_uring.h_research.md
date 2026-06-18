<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/include/liburing/io_uring.h -->
## sources/test-tools/liburing/src/include/liburing/io_uring.h

Purpose: this is the copied/shared Linux UAPI definition for io_uring. It defines the binary contract for submission queue entries, completion queue entries, ring setup parameters, feature bits, opcodes, register opcodes, resource-registration structures, provided-buffer rings, wait arguments, zero-copy receive configuration, BPF/filter/query-facing structures, and command-specific flags.

Important APIs/types/functions: key types are `io_uring_sqe`, `io_uring_cqe`, `io_sqring_offsets`, `io_cqring_offsets`, `io_uring_params`, `io_uring_rsrc_register`, `io_uring_rsrc_update*`, `io_uring_probe*`, `io_uring_restriction`, `io_uring_buf`, `io_uring_buf_ring`, `io_uring_buf_reg`, `io_uring_reg_wait`, `io_uring_getevents_arg`, `io_uring_sync_cancel_reg`, `io_uring_zcrx_*`, and `zcrx_ctrl`. Important enums/defines include `IORING_OP_*`, `IOSQE_*`, `IORING_SETUP_*`, `IORING_FEAT_*`, `IORING_REGISTER_*`, CQE flags, enter flags, timeout/cancel/poll/send/recv/accept flags, and fixed-file allocation constants.

Control flow: there is no executable flow. The file describes how userspace populates an SQE and how the kernel returns CQEs and setup offsets. `io_uring_setup` fills `io_uring_params`; liburing maps ring regions using offset fields; `io_uring_register` consumes the register argument structs by opcode.

State and persistence behavior: the structs model shared kernel/userspace state. Ring offsets, head/tail indices, CQ flags, registered resources, provided buffer rings, and zero-copy receive objects persist for the lifetime of the ring or registered object.

Dependencies and integration points: includes Linux types, fs definitions, and optionally `linux/time_types.h`. `liburing.h`, `setup.c`, `queue.c`, and `register.c` rely on field names and flag values exactly matching the kernel. Tests use many feature flags and opcodes to gate behavior.

Risks: this file is ABI-critical. Padding, union layout, numeric opcode/register values, and bit assignments must track the kernel UAPI. Changing it without matching kernel support can cause silent request misinterpretation. Mixed 32-byte CQE and 128-byte SQE modes add index and skip-entry complexity.

Test signals: the accept, fixed-file, registered wait, buffer-ring, and syzkaller tests serve as regression signals for specific UAPI combinations. Build failures here are usually broad because the public header and C sources include this file everywhere.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/include/liburing/io_uring.h -->

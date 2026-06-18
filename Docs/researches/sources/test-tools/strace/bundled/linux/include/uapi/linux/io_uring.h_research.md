# sources/test-tools/strace/bundled/linux/include/uapi/linux/io_uring.h

Purpose: declares the core `io_uring` userspace ABI for setup, mmap ring offsets, SQE/CQE layouts, submission opcodes, completion flags, enter/register flags, probe data, registered resources, provided buffers, NAPI, socket uring commands, and newer zcrx/query integration.

Important APIs/types/functions: central types are `io_uring_sqe`, `io_uring_cqe`, `io_uring_params`, `io_sqring_offsets`, `io_cqring_offsets`, `io_uring_register_op`, `io_uring_op`, resource registration/update structures, restriction structures, provided-buffer ring types, `io_uring_getevents_arg`, and `io_uring_sync_cancel_reg`.

Control flow: applications call `io_uring_setup`, mmap SQ/CQ/SQE regions using the exported offsets, fill SQEs using opcode-specific union fields, submit/wait with `io_uring_enter`, and configure shared kernel state with `io_uring_register`. CQEs return `res`, `user_data`, and flags for buffers, multishot, notification, skip, and large-CQE modes.

State/persistence behavior: rings persist as kernel objects behind fds or registered ring indexes. Registered files, buffers, personalities, provided-buffer groups, NAPI settings, clocks, zcrx interfaces, and memory regions survive across submissions until unregistered or fd close.

Dependencies/integration: includes `linux/fs.h`, `linux/types.h`, optional `linux/time_types.h`, and `linux/io_uring/zcrx.h`. strace integration must decode three syscalls plus many register op argument structs and SQE opcode fields.

Risks and test signals: dense unions make field interpretation opcode-dependent. Tests should cover setup feature flags, mixed SQE/CQE sizing, fixed fd allocation, registered-ring flags, probe output, buffer rings, zcrx registration, and endian-sensitive poll fields.

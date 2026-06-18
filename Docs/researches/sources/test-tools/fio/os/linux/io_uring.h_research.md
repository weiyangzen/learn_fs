# sources/test-tools/fio/os/linux/io_uring.h

## Purpose
`io_uring.h` vendors the Linux userspace ABI definitions needed by fio's io_uring engine. It lets fio build against systems whose libc/kernel headers may not expose all of the io_uring structures, opcodes, setup flags, feature flags, mmap offsets, and registration commands that fio wants to use or probe.

## Important APIs, Types, and Functions
Important ABI types are `struct io_uring_sqe`, `struct io_uring_cqe`, `struct io_sqring_offsets`, `struct io_cqring_offsets`, `struct io_uring_params`, resource registration/update structs, probe structs, restrictions, PI attributes, and `struct io_uring_getevents_arg`. Important constants include `IORING_OP_*`, `IOSQE_*`, `IORING_SETUP_*`, `IORING_ENTER_*`, `IORING_FEAT_*`, `IORING_REGISTER_*`, CQE/SQ ring flags, mmap offsets, timeout/poll/splice/fsync flags, and `IORING_REGISTER_FILES_SKIP`.

## Control Flow
There is no executable code. The structs define the memory layout shared with Linux syscalls: users fill SQEs, map rings using offsets returned in `io_uring_params`, read CQEs, and pass registration/probe structs to `io_uring_register()`.

## State and Persistence
Runtime state lives in kernel-created rings and userspace mappings described by these structs. The header persists no state itself, but layout mistakes would corrupt submission/completion interpretation.

## Dependencies and Integration Points
It depends on Linux UAPI types from `<linux/fs.h>` and `<linux/types.h>`. fio's io_uring engine, feature probing, registered file/buffer handling, polling, SQ/CQ sizing, PI attributes, and newer command support depend on this ABI matching the kernel.

## Risks and Edge Cases
Because this mirrors a moving kernel ABI, stale definitions can hide or misdescribe newer flags. Flexible array members and packed fields must match kernel layout across architectures. Optional features such as SQE128/CQE32, registered-ring FDs, mixed CQEs, PI attributes, and fixed uring commands must be gated by kernel feature/probe results before use.

## Test Signals
Build tests on older and newer Linux headers, io_uring engine smoke tests, feature-probe validation, fixed-buffer/file registration tests, CQE size variants, and syscall failure handling on kernels lacking specific flags are the strongest signals.

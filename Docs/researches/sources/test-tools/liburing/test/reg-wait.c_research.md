# sources/test-tools/liburing/test/reg-wait.c

Purpose: validates registered wait argument memory regions for `io_uring_submit_and_wait_reg()` and direct `io_uring_enter2` registered wait offsets. It exercises user-provided regions, kernel-allocated regions, disabled-ring requirements, signal mask validation, bounds checks, huge page cases, and mapping types.

Important APIs and types: `struct io_uring_reg_wait`, `struct io_uring_region_desc`, `struct io_uring_mem_region_reg`, `IORING_MEM_REGION_REG_WAIT_ARG`, `IORING_MEM_REGION_TYPE_USER`, `IORING_REG_WAIT_TS`, `IORING_ENTER_EXT_ARG_REG`, `io_uring_register_region`, `io_uring_submit_and_wait_reg`, `io_uring_enable_rings`, `__sys_io_uring_enter2`, and mmap flags including huge pages.

Control flow: `test_regions()` verifies registration only succeeds on disabled rings, rejects null, zero-size, misaligned, bogus, read-only, and invalid kernel/user combinations, and records whether kernel-allocated regions are supported. `test_wait_arg()` registers one page of user memory as wait args, enables the ring, then runs `test_basic()` for timeout duration, `test_invalid_sig()` for bad sigmask size/address, and `test_offsets()` for first, last, one-past-end, overflow, and unaligned offsets. `test_region_buffer_types()` repeats offset checks over user memory, huge pages where available, and kernel-created regions of several sizes.

State and persistence: global `page_size` and `reg` define the active wait-argument memory. Registered memory persists across waits until ring exit. `struct t_region` tracks whether memory is user or kernel mapped and its size.

Dependencies and integration: requires registered memory-region support; unsupported region registration skips. Huge-page cases tolerate `-ENOMEM` and `-EINVAL`. Direct syscall wrapper is used for offset tests not exposed by the high-level helper.

Risks and test signals: wrong timeout duration, invalid signal handling, accepting out-of-bounds offsets, or registration accepting invalid memory all fail. Passing proves registered wait arguments are safely bounded and work across memory backends.

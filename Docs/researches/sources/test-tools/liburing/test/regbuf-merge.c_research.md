# sources/test-tools/liburing/test/regbuf-merge.c

Purpose: syzkaller-derived regression reproducer for buffer registration/merge behavior through raw syscalls and fixed mappings. It is disabled under sanitizer builds because it relies on fixed virtual addresses and low-level memory manipulation.

Important APIs and types: raw `io_uring_setup` and `io_uring_register` syscalls, manual `mmap` of SQ/CQ rings and SQEs, `struct io_uring_params`, `IORING_OFF_SQ_RING`, `IORING_OFF_SQES`, and hard-coded ring offset constants. `syz_io_uring_setup()` wraps setup and maps rings at supplied addresses.

Control flow: when sanitizers are not enabled, `main()` maps guard and data regions at syzkaller-style fixed addresses, writes a crafted `io_uring_params` structure, calls `syz_io_uring_setup()` with 0x2fd6 entries and fixed mapping addresses, stores the returned fd if setup succeeded, writes a small registration descriptor at another fixed address, and invokes `io_uring_register` opcode 0 with two entries. The program returns pass as long as it does not crash.

State and persistence: global `r[0]` stores the ring fd or all-ones fallback. All interesting state is laid out in fixed virtual memory, mirroring a minimized fuzz reproducer rather than normal liburing abstractions.

Dependencies and integration: depends on architecture/syscall numbers and Linux io_uring mmap ABI. Under `CONFIG_USE_SANITIZER`, `main()` skips to avoid sanitizer conflicts with fixed mappings.

Risks and test signals: this is a crash regression test, not a semantic assertion test. Passing means the kernel tolerates the crafted setup/register sequence without process-visible failure; crashes or fatal signals indicate memory-management regressions in buffer registration paths.

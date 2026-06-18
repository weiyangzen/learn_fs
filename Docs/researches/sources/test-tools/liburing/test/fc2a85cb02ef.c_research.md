<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/fc2a85cb02ef.c -->
## sources/test-tools/liburing/test/fc2a85cb02ef.c

Purpose: syzkaller-derived fault-injection regression for io_uring registration under allocation/futex failure conditions.

Important APIs/types/functions: `write_file`, `setup_fault`, `inject_fault`, raw `__sys_io_uring_setup`, raw `__sys_io_uring_register`, `/proc/thread-self/fail-nth`, and debugfs fault knobs.

Control flow: the test maps a fixed userspace area, enables relevant fault injection controls, initializes a large `io_uring_params` blob in mapped memory, sets up a ring through the raw syscall, opens an unusual socket, injects the next failure point, and calls raw io_uring register opcode 2 with one fd.

State and persistence behavior: depends on kernel debugfs fault-injection state and writes to system fault-control files. It leaves most syscall results unchecked because the regression is crash/leak oriented.

Dependencies and integration points: requires fail-slab/fail-futex/fail-page-alloc support and permission to write debugfs/proc fault controls.

Risks: environment-specific and privileged; skipped when fault injection is unavailable. It intentionally uses fixed addresses and raw syscalls.

Test signals: pass means the crafted failing register path returns without crashing the process/kernel.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/fc2a85cb02ef.c -->

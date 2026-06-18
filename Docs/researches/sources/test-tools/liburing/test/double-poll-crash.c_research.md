# sources/test-tools/liburing/test/double-poll-crash.c

Purpose: syzkaller-derived low-level reproducer for a double-poll/io_uring crash. Important APIs are raw `__sys_io_uring_setup`, manual ring/SQE `mmap`, hand-written SQ tail/array submission, `__sys_io_uring_enter`, `syz_open_dev`, and device `ioctl`.

Control flow: x86 non-sanitizer builds map fixed virtual memory, set up a raw ring, open a character device, construct and submit a raw SQE, enter the ring, and issue a crafted ioctl. State is raw kernel ring/device state; no normal liburing abstractions. Signal is survival without crash. Risks are architecture/layout brittleness and device availability.

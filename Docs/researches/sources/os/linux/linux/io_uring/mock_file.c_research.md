# File Research: sources/os/linux/linux/io_uring/mock_file.c

Testing-only misc device that creates artificial files for io_uring edge-case testing.

Key behavior:
- Misc device `/dev/io_uring_mock` exposes `.uring_cmd` manager commands gated by `CAP_SYS_ADMIN`.
- Probe command returns mock feature support.
- Create command taints the kernel with `TAINT_TEST`, validates `io_uring_mock_create`, and returns an anon-inode file with configurable size, optional NOWAIT support, optional poll support, and optional delayed read/write completion.
- Mock read/write either complete immediately by zeroing/advancing iterators or return `-EIOCBQUEUED` and complete later from an hrtimer.
- Mock file `.uring_cmd` supports copying between fixed registered buffers and user memory via `io_uring_cmd_import_fixed_vec()`.

Important details:
- File size is capped at 1 GiB and delay at 1 second.
- Pollable mock files always advertise readable and writable readiness.
- Release frees `struct io_mock_file`; timer allocations are freed after completion.

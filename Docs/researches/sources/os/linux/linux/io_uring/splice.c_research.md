# File Research: sources/os/linux/linux/io_uring/splice.c

io_uring splice and tee operation implementation.

Key responsibilities:
- Prepares splice/tee SQEs, validating splice flags and forcing async execution.
- Supports normal input fds and fixed input files via `SPLICE_F_FD_IN_FIXED`.
- Executes `do_splice()` and `do_tee()` with requested offsets and length.
- Cleans up fixed-file resource references after use.

Important data flows:
- Prep stores output file from the request, input fd/index, offsets, length, and flags.
- Fixed input lookup increments the resource node ref under submit lock and marks request cleanup.
- Issue calls the VFS splice/tee helper if `len` is nonzero, releases normal fd refs or leaves fixed refs to cleanup, and completes with byte count or error.

Important invariants:
- These operations are always forced async and warn if issued in nonblocking mode.
- `tee` rejects explicit offsets.
- A return shorter than requested length marks the request failed.

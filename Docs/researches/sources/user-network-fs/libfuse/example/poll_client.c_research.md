# sources/user-network-fs/libfuse/example/poll_client.c

## Purpose
`poll_client.c` is a small userspace test client for `poll.c`. It opens the sixteen files `0` through `F`, waits for readiness with `select()`, reads ready files, and prints per-file read counts.

## Important APIs, Types, and Functions
The program uses `open`, `select`, `FD_SET`, `FD_ISSET`, and `read`. It has only `main()`, a `hex_map` of file names, an fd array, and a fixed read buffer.

## Control Flow
`main()` opens each hex-named file in the current directory, computes `nfds` from the last opened fd plus one, then performs sixteen select/read iterations. For each iteration, it builds a read fd set, blocks indefinitely in `select`, prints `_:` for not-ready files, and reads/prints the byte count for ready files.

## State and Persistence
State is limited to process-local file descriptors and the stack/static read buffer. It does not write data and leaves persistence entirely to the mounted FUSE example.

## Dependencies and Integration Points
It assumes the current working directory is the root of a mounted `poll.c` filesystem. It depends on POSIX `select` and file descriptors small enough for `fd_set`. It exercises FUSE poll readiness by reading every descriptor that select reports.

## Risks
The program never closes fds explicitly, relying on process exit. `nfds` is computed from the last fd rather than the maximum across all fds, which is usually fine because opens are sequential but not guaranteed by API. It uses `select`, so very high-numbered fds beyond `FD_SETSIZE` would be unsafe.

## Test Signals
When run against `poll.c`, output should show changing readiness across files and positive byte counts. Running outside the mount should fail on `open`. Repeated runs should confirm the server's one-open-per-file policy releases handles on process exit.

# sources/user-network-fs/libfuse/example/null.c

## Purpose
`null.c` implements a single-file FUSE filesystem meant to be mounted on a regular file rather than a directory. Reads return zero-filled data up to a synthetic 4 GiB size, writes are discarded while reporting success, and truncate is accepted without changing size. The file also demonstrates the libfuse service API path for systemd socket activation.

## Important APIs, Types, and Functions
The high-level operation table `null_oper` registers `getattr`, `truncate`, `open`, `read`, and `write`. The service path uses `fuse_service_accept()`, `fuse_service_accepted()`, `fuse_service_append_args()`, `fuse_service_finish_file_requests()`, `fuse_service_expect_mount_format(S_IFREG)`, `fuse_service_main()`, `fuse_service_send_goodbye()`, and `fuse_service_exit()`. Non-service execution validates the mountpoint with `stat()` and calls `fuse_main()`.

## Control Flow
`main()` first tries to accept a FUSE service connection. If accepted, `null_service()` appends service-supplied arguments, finishes file requests, declares that the mount target should be a regular file, loosens mode to `0666`, runs `fuse_service_main`, sends goodbye, and exits through the service helper. If no service was accepted, it parses command-line options, requires a mountpoint, verifies that the mountpoint is a regular file, and calls `fuse_main`. Operations only accept path `/`; other paths return `ENOENT`.

## State and Persistence
The only mutable state is process-global `mode`, initially `0644` and changed to `0666` in service mode. File contents are not stored; reads synthesize zero bytes and writes discard input. Attribute times are generated from `time(NULL)` on each getattr. There is no persistence across process restarts.

## Dependencies and Integration Points
This example depends on high-level libfuse, `fuse_service.h`, standard libc, and a systemd socket/service pair when run in service mode. It expects service-managed mounts to target a file (`S_IFREG`) instead of a directory. Non-service mode depends on the caller providing an existing regular file mountpoint.

## Risks
`null_read()` only checks `offset >= 4GiB`; if `offset + size` exceeds 4 GiB it still returns the full requested size, so reads can report bytes beyond the advertised EOF. The Doxygen include line names `passthrough_fh.c`, probably a copy/paste mistake. Service mode changes permissions to world writable because dynamic users cannot predict ownership, which is correct for the example but unsuitable for sensitive data paths.

## Test Signals
Compile with `pkg-config fuse3`, create a regular file as mountpoint, mount, and verify `stat` reports a 4 GiB regular file. `dd if=<mountpoint>` should return zero bytes, and writes should report the written count without persisting data. Service-mode tests should use the matching socket/service unit and confirm `fuse_service_expect_mount_format(S_IFREG)` rejects directory mounts.

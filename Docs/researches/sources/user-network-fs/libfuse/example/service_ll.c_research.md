# sources/user-network-fs/libfuse/example/service_ll.c

## Purpose
`service_ll.c` is the low-level API counterpart to `service_hl.c`. It demonstrates a systemd-managed FUSE service that exposes one file backed by a caller-provided device or file while using explicit low-level sessions and replies.

## Important APIs, Types, and Functions
`struct service_ll` stores `struct fuse_session *`, device path, `struct fuse_service *`, and debug flag. `service_ll_oper` combines low-level helper callbacks (`single_file_ll_lookup`, `getattr`, `setattr`, `readdir`, `open`, `statfs`, `statx`, `fsync`) with local `init`, `read`, and `write`. `service_ll_opt_proc()` delegates shared single-file options and captures the device argument.

## Control Flow
`main()` accepts service activation, appends args, parses service and FUSE command-line options, handles help/version, validates mountpoint and device, obtains the backing file through `single_file_service_open()`, finishes file requests, configures `single_file`, creates a low-level session, mounts via `fuse_service_session_mount()`, sends goodbye/releases the service object once mounted, and runs the chosen loop. `service_ll_read()` allocates a reply buffer, clamps reads, calls `single_file_pread()`, and replies with `fuse_reply_buf()`. `service_ll_write()` clamps writes, calls `single_file_pwrite()`, and replies with `fuse_reply_write()`.

## State and Persistence
Runtime state is the `ll` singleton, low-level session, loop config, and global `single_file`. Persistent data lives in the backing file/device. `service_ll_init()` sets `conn->time_gran = 1`; single-file metadata timeouts are zero in the helper.

## Dependencies and Integration Points
The file depends on low-level libfuse, `fuse_service.h`, and `single_file.c/h`. It integrates with systemd service activation, service-mediated file transfer, standard low-level session setup, and both single-threaded and multi-threaded FUSE loops.

## Risks
The low-level read path allocates `count` bytes after clamping; very large but valid reads can pressure memory. Direct I/O policy returns `ENOSYS` when disallowed. Error sign handling differs between helper functions and low-level replies, so the code carefully negates helper returns; regressions here would surface as wrong errno values. It sends goodbye/release before entering the loop once mounted, so later errors are ordinary session failures rather than service-handshake failures.

## Test Signals
Mount through `service_ll.socket`, read/write the single file, verify read-only, size, blocksize, direct-I/O, and sync options. Compare high-level and low-level behavior for metadata, statx, fsync, and error returns. Test single-thread and multi-thread options and unmount cleanup.

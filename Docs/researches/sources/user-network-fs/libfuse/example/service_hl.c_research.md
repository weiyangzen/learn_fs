# sources/user-network-fs/libfuse/example/service_hl.c

## Purpose
`service_hl.c` is a high-level API example for a systemd-managed FUSE service. It exposes a single regular file backed by a caller-provided device or file, using the shared `single_file` helper for metadata/options and service-mediated file acquisition.

## Important APIs, Types, and Functions
`struct service_hl` stores the requested device path, `struct fuse_service *`, and debug flag. `service_hl_oper` combines helper callbacks (`single_file_hl_getattr`, `readdir`, `open`, `opendir`, `statfs`, `chmod`, `utimens`, `fsync`, `chown`, `truncate`, `statx`) with local `init`, `read`, and `write`. `service_hl_opt_proc()` delegates to `single_file_opt_proc()` and captures the first non-option as `hl.device`.

## Control Flow
`main()` accepts only service activation, appends service args, parses options, requires a device argument, requests and receives the backing file through `single_file_service_open()`, finishes service file requests, configures `single_file`, declares a directory mount format, and calls `fuse_service_main()`. Reads and writes verify the path/open file handle, enforce direct-I/O policy, clamp operations to the configured size, and call `single_file_pread()` or `single_file_pwrite()`.

## State and Persistence
Service-local state is `hl` and the global `single_file` object from `single_file.c`. Persistent data lives in the opened backing file or block device. Metadata such as mode, timestamps, size, block count, and read-only/direct-I/O settings are held in memory and initialized by `single_file_configure()`.

## Dependencies and Integration Points
The file depends on high-level libfuse, `fuse_service.h`, pthread-aware single-file helpers, Linux filesystem headers for block/device metadata, and the matching systemd socket/service units. It integrates with the mount caller's environment by asking the service layer to provide the backing file rather than opening it directly inside the sandbox.

## Risks
The program refuses non-service execution, so running it directly exits early. Read/write return `ENOSYS` when direct I/O is requested but disallowed; clients must handle that. The backing file is opened with exclusive flags in the helper, which may fail under concurrent use. The high-level path checks depend on `fi->fh` being set by helper open/opendir callbacks.

## Test Signals
Install the matching socket/service units, start the socket, and mount with `mount -t fuse.service_hl <device> <mnt>`. Verify directory listing exposes the configured single file, reads/writes map to the backing file, read-only mode rejects writes, `size=` clamps I/O, `statx` reports configured metadata, and service teardown calls `single_file_close()`.

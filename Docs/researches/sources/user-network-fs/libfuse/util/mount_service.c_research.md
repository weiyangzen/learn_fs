# sources/user-network-fs/libfuse/util/mount_service.c

## Purpose
Client-side helper for service-managed FUSE filesystems. It connects to a subtype-specific Unix socket, sends argv and required fds, services filesystem daemon requests to open files/devices and provide mount parameters, and performs the final privileged mount.

## Important APIs, Types, And Functions
- `struct mount_service` tracks subtype, source, mountpoint strings, options, socket, `/dev/fuse`, argv memfd, mountpoint fd, fsopen fd, and mount status.
- `mount_service_subtype`, `mount_service_present`, and `mount_service_main` are exported through `mount_service.h`.
- Packet helpers `__send_packet`, `__recv_packet`, `__send_fd`, and command handlers implement the service protocol.
- Command handlers cover hello, open/open-bdev, fsopen, source, mntopts, mtabopts, mountpoint, mount, and bye.
- `mount_service_regular_mount` uses `mount(2)`; `mount_service_fsopen_mount` uses new mount API when available.

## Control Flow
Startup parses `-t`, derives subtype, connects to `FUSE_SERVICE_SOCKET_DIR/<subtype>` with dropped privileges, negotiates protocol bounds, captures arguments in a memfd, opens `/dev/fuse`, sends both fds to the service, then enters a packet loop. The service can request path opens, source/options setup, mountpoint attachment, and final mount. Mountpoint attachment opens and pins the target, resolves the path for mtab, and uses `.` or `/dev/fd/<n>` to reduce path races. Final mount revalidates the fd, applies non-root policy, tries fsopen/fsmount if prepared, and falls back to `mount(2)` when necessary.

## State And Persistence
Persistent effects are the final FUSE mount and optional mtab/utab update. Runtime state includes a connected Unix seqpacket socket, memfd argv image, fd-passed `/dev/fuse`, pinned mountpoint fd, and optional fsopen context. The destructor closes fds, shuts down the socket, and frees all strings.

## Dependencies And Integration Points
Used by `fuservicemount3` and optionally by `mount.fuse3`. Depends on `fuse_service_priv.h` packet definitions, `mount_util.c`, `fuser_conf.c`, optional `mount_fsmount.c`, service socket directory configuration, memfd, Unix sockets, and Linux block-device ioctls.

## Risks
The protocol crosses a trust boundary with a filesystem service. The code disables receiving fds from the service, bounds packet size, checks null terminators and padding, requires the mountpoint to appear in argv, and enforces non-root access controls. Residual risk remains around mountpoint fd/path behavior, service-requested open paths, and fsopen fallback parity. Non-root unsafe mount flags are adjusted rather than fatal, so tests must confirm final flags.

## Test Signals
Protocol tests should cover wrong packet sizes, bad magic, unsupported versions, path separators in subtype, socket absence fallback, fd-passing failures, open/open-bdev errors, mountpoint not in argv, repeated source/options/mountpoint commands, non-root allow_other rejection, mount count limits, fsopen fallback, mtab `-n`, and cleanup after service bye/failure.

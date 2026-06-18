# sources/user-network-fs/libfuse/example/service_hl@.service

## Purpose
`service_hl@.service` is the sandboxed systemd service template for the high-level single-file FUSE example.

## Important APIs, Types, and Functions
The service uses `Type=exec`, placeholder `ExecStart=/path/to/service_hl`, `DynamicUser=true`, strict filesystem/network/device/proc protections, syscall filters, no capabilities, `NoNewPrivileges=true`, `UMask=7777`, ttyprintk logging, and `OOMPolicy=continue`.

## Control Flow
Socket activation starts one instance per accepted service connection. The service binary accepts the service socket, requests its backing file/device from the mount caller, runs the high-level FUSE service loop, sends goodbye, and exits. `CollectMode=inactive-or-failed` avoids stale failed-unit accumulation.

## State and Persistence
Systemd manages dynamic identity, namespaces, resource limits, and logging. The unit intentionally provides little writable state; the FUSE service obtains its backing resource through the service protocol.

## Dependencies and Integration Points
The unit depends on replacing `ExecStart`, on systemd sandbox features, and on the paired socket unit. It is tuned for libfuse service operation and allows `mbind`/`sched_setaffinity` for libfuse io_uring behavior despite other syscall restrictions.

## Risks
The sandbox can block future libfuse or backing-file behavior if new syscalls or filesystem access are required. `UMask=7777` and no capabilities are deliberately restrictive. Logging to `/dev/ttyprintk` may not be available in all environments.

## Test Signals
Verify the unit with `systemd-analyze verify`, start through the socket, inspect `systemctl status` for dynamic-user sandboxing, and mount/unmount a high-level service filesystem. A syscall-filter violation should surface as `EL3RST`.

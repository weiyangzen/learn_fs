# sources/user-network-fs/libfuse/example/service_ll@.service

## Purpose
`service_ll@.service` is the sandboxed systemd template for the low-level single-file FUSE service.

## Important APIs, Types, and Functions
It has the same hardening profile as the high-level and null service templates: `Type=exec`, placeholder `ExecStart=/path/to/service_ll`, dynamic user, strict system/home/device/network/proc/kernel protections, syscall allow/deny filters, no capabilities, no new privileges, restrictive umask, ttyprintk logging, and OOM behavior set to continue.

## Control Flow
The paired socket starts an instance for each accepted connection. `service_ll` accepts the socket, negotiates resources, mounts a low-level FUSE session, releases the service handshake, and then handles FUSE requests until unmount.

## State and Persistence
The unit creates transient process, namespace, dynamic-user, and logging state. It intentionally avoids general writable state; backing data is provided through the FUSE service protocol instead of direct host access.

## Dependencies and Integration Points
It depends on systemd sandboxing and a corrected `ExecStart`. The syscall filter includes accommodations for libfuse io_uring. It integrates with `service_ll.socket.in` and `service_ll.c`.

## Risks
The placeholder binary path must be changed. Sandbox restrictions may need updates if libfuse, the C library, or deployment environment requires additional syscalls or devices. `RestrictFileSystems=` is empty, which intentionally leaves the directive present but not listing allowed filesystem types.

## Test Signals
`systemd-analyze verify` should pass after path substitution. Socket-activated mounting should run under the dynamic user with no capabilities. Kernel/syslog output should capture service diagnostics, and syscall filter hits should produce `EL3RST`.

# sources/user-network-fs/libfuse/example/null@.service

## Purpose
`null@.service` is the systemd service template for running the `null` sample as a heavily sandboxed socket-activated FUSE server. It is intended to be paired with `null.socket.in`.

## Important APIs, Types, and Functions
Important service directives include `Type=exec`, `ExecStart=/path/to/null`, `DynamicUser=true`, `ProtectSystem=strict`, `PrivateTmp=true`, `PrivateDevices=true`, `PrivateUsers=true`, `PrivateNetwork=true`, `RestrictAddressFamilies=none`, `SystemCallFilter` allow/deny lists, empty `CapabilityBoundingSet`, `NoNewPrivileges=true`, `UMask=7777`, `DevicePolicy=closed`, and `OOMPolicy=continue`.

## Control Flow
For each accepted socket connection, systemd starts an instance of this template. The process runs the `null` binary, which detects service activation with `fuse_service_accept()`, requests/finishes service file handling, runs the FUSE main loop, sends goodbye, and exits. `CollectMode=inactive-or-failed` prevents failed units from accumulating.

## State and Persistence
State is managed by systemd: transient dynamic user identity, sandbox namespaces, logs to `/dev/ttyprintk`, and the unit lifecycle. No writable filesystem state is intentionally available because `ProtectSystem=strict`, `ProtectHome=true`, `UMask=7777`, and no capabilities constrain the process.

## Dependencies and Integration Points
The unit depends on a valid `ExecStart` path, systemd sandboxing features, `/dev/ttyprintk` for output, and the libfuse service protocol over the socket unit. The comments account for libfuse io_uring needing `mbind` and `sched_setaffinity`.

## Risks
The placeholder `ExecStart=/path/to/null` must be replaced. The syscall filter and namespace restrictions are intentionally strict and may break future libfuse behavior if it needs new syscalls or filesystem visibility. `StandardOutput=append:/dev/ttyprintk` depends on that device existing and being usable in the sandbox.

## Test Signals
`systemd-analyze verify null@.service` should pass after replacing `ExecStart`. Starting through `null.socket` should spawn instances under a dynamic user with no capabilities. Journal or ttyprintk output should show service startup and teardown, and syscall-filter failures should return `EL3RST`.

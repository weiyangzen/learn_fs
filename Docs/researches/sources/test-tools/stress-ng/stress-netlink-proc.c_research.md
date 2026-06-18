# sources/test-tools/stress-ng/stress-netlink-proc.c

## Purpose
`stress-netlink-proc.c` implements the `netlink-proc` stressor. It subscribes to Linux process connector events over `NETLINK_CONNECTOR`, creates short process chains, and counts recognized process events. This exercises connector delivery, process event parsing, fork/exit activity, and capability-gated netlink paths.

## Important APIs, Types, and Functions
The exported `stress_netlink_proc_info` registers the stressor with `CLASS_OS` and a `supported` callback. `stress_netlink_proc_supported()` requires `CAP_NET_ADMIN` through `stress_capabilities_check(SHIM_CAP_NET_ADMIN)`. `monitor()` receives and parses netlink messages, validating `nlmsghdr`, `cn_msg`, and `proc_event` payloads. `spawn_several()` recursively forks a bounded chain of children and changes process names to produce fork, exec-like name, wait, and exit activity. `stress_netlink_proc()` opens, binds, subscribes, runs, and closes the connector socket.

## Control Flow
The stressor creates a `PF_NETLINK`, `SOCK_DGRAM`, `NETLINK_CONNECTOR` socket and binds it to the process connector group using the current PID and `CN_IDX_PROC`. It builds a three-element `writev()` message containing an `nlmsghdr`, a `cn_msg` addressed to the process connector, and a `PROC_CN_MCAST_LISTEN` operation. After the global sync point, the run loop calls `spawn_several(args->name, 0, 5)` and then `monitor()`. `monitor()` receives one buffer, skips errors and no-op messages, validates connector IDs and payload sizes, and increments the bogo counter for recognized `PROC_EVENT_*` variants available for the compile-time kernel header version.

## State and Persistence
State is limited to the netlink socket and transient forked child processes. No process subscription state is explicitly unsubscribed before close; closing the socket releases it. Bogo counts are event driven and depend on kernel connector delivery. The process-name changes are transient per child.

## Dependencies and Integration Points
The stressor depends on Linux connector, netlink, and process connector headers, plus `writev`, `recv`, `fork`, and wait helpers. It integrates with stress-ng capability checks, logging, process naming, sync start, run-state transitions, and bogo counters. The event switch is guarded by `LINUX_VERSION_CODE` so the source can compile against older headers with fewer `PROC_EVENT_*` constants.

## Risks
This stressor will skip without `CAP_NET_ADMIN` or when the connector subsystem is unavailable. Netlink receive can drop events with `ENOBUFS`, which is treated as non-fatal, so bogo counts are not a complete process-event audit. `spawn_several()` recursively forks up to a small fixed depth, but repeated runs still create process churn and can interact with low `RLIMIT_NPROC`. The monitor reads one buffer per iteration, so high event rates can be coalesced or partially ignored.

## Test Signals
Validate unsupported behavior as an unprivileged user and event counting as a privileged user or with `CAP_NET_ADMIN`. Short runs should report bogo events and exit cleanly on timeout. Kernel/header compatibility tests should compile with and without connector headers and with older `LINUX_VERSION_CODE` definitions.

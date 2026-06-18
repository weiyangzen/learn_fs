# sources/test-tools/stress-ng/stress-netlink-task.c

## Purpose
`stress-netlink-task.c` implements the `netlink-task` stressor. It uses generic netlink taskstats to repeatedly query task statistics for the running process, validating selected payload fields and exercising netlink request/response handling for task accounting.

## Important APIs, Types, and Functions
The stressor exports `stress_netlink_task_info` with `CLASS_OS`, `VERIFY_ALWAYS`, and a capability-based supported callback. `stress_nlmsg_t` is a compact message structure containing `nlmsghdr`, `genlmsghdr`, and 1 KiB payload storage. `stress_netlink_sendcmd()` builds and sends generic netlink commands with one attribute. `stress_parse_payload()` walks nested taskstats attributes and verifies the returned PID and monotonic non-decrease of `nivcsw`. `stress_netlink_taskstats_monitor()` sends repeated `TASKSTATS_CMD_GET` requests and parses replies. `stress_netlink_task()` opens the socket, discovers the taskstats family id, and enters the monitor loop.

## Control Flow
The stressor creates an `AF_NETLINK`, `SOCK_RAW`, `NETLINK_GENERIC` socket, binds it, then sends `CTRL_CMD_GETFAMILY` for `TASKSTATS_GENL_NAME`. It receives the family response, expects a `CTRL_ATTR_FAMILY_ID` attribute after the first attribute, and stores that id. After synchronization it repeatedly invokes `stress_netlink_taskstats_monitor()`. Each monitor iteration sends `TASKSTATS_CMD_GET` with `TASKSTATS_CMD_ATTR_PID` for the current process, receives a `stress_nlmsg_t`, checks `NLMSG_OK`, walks generic netlink attributes, and parses `TASKSTATS_TYPE_AGGR_PID` payloads. Every parsed response increments the bogo counter.

## State and Persistence
The stressor maintains only the socket, discovered family id, and the last seen involuntary context switch count. There are no durable writes. Any taskstats accounting consumed is kernel-provided runtime state. The `nivcsw` variable persists across monitor iterations to detect unexpected counter regressions.

## Dependencies and Integration Points
This is Linux-specific and requires connector, netlink, cn_proc, genetlink, and taskstats headers, plus `__linux__` generic netlink support. It depends on `CAP_NET_ADMIN`. It integrates with stress-ng state transitions, sync start, bogo counting, logging, and unimplemented-stressor metadata. It uses stress-ng shim memory helpers and branch annotations.

## Risks
The generic netlink family id parser assumes a particular attribute order in the family response by advancing to the second attribute and checking `CTRL_ATTR_FAMILY_ID`; more defensive parsing would walk all attributes. `stress_netlink_sendcmd()` returns success for `EAGAIN` and `EINTR`, so monitor logic may proceed to receive even if a request was not actually sent. Payload parsing uses kernel-structured data and careful length checks, but malformed or unexpected nested attributes can stop parsing early. The `numa_cpus` style bug is not present here, but capability and kernel config availability strongly affect runtime coverage.

## Test Signals
Run as unprivileged and privileged users to confirm skip and active paths. A short privileged run should count taskstats responses without PID mismatch or `nivcsw` regression messages. Tests should include kernels where taskstats generic netlink is absent, and builds without one or more required headers to verify the unimplemented path.

# File Research: sources/virtualization/nbd/tests/run/libnl_mock.c

## Purpose
Implements an `LD_PRELOAD` libnl mock used by runtime tests to validate and simulate NBD generic-netlink operations without requiring real kernel netlink behavior.

## Main Entry Points
- `init_real_functions()` resolves real libnl symbols with `dlsym(RTLD_NEXT)`.
- Validation helpers inspect outgoing netlink messages for connect, disconnect, reconfigure, and status commands.
- Overridden libnl functions such as `genl_connect()`, `genl_ctrl_resolve()`, `nl_send_auto()`, `nl_wait_for_ack()`, and `nl_recvmsgs_default()` provide controlled mock behavior.
- Public helpers `mock_set_device_status()`, `mock_set_device_index()`, and `mock_send_link_dead_notification()` allow tests to manipulate mock state.

## Control Flow
The mock returns fixed family/group IDs for `nbd` and `nbd_mc_group`. Outgoing messages are intercepted in `nl_send_auto()`, parsed, and checked for required attributes. Connect validation checks size, block size, server flags, sockets, and optional dead-connection timeout. Disconnect and reconfigure require device index and, for reconfigure, sockets. Status requests record the queried index. `nl_recvmsgs_default()` fabricates a status response and invokes the registered callback.

## Dependencies
Depends on libdl, libnl headers/APIs, Linux netlink headers, and local `nbd-netlink.h`.

## Risks and Notes
Callback role detection in `nl_socket_modify_cb()` is heuristic: the first custom valid callback is treated as status and the next as persist. `nl_socket_get_fd()` returns fake fd `42`, so tests must avoid paths that require a real pollable descriptor. The mock both calls real allocation/parsing helpers and suppresses actual netlink sending.

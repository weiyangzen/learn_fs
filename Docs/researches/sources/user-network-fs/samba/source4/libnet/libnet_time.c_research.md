# sources/user-network-fs/samba/source4/libnet/libnet_time.c

## Purpose

`libnet_time.c` retrieves a remote server's time-of-day through SRVSVC `NetRemoteTOD` and exposes it through the libnet `RemoteTOD` dispatcher.

## Important APIs, Types, and Functions

`libnet_RemoteTOD()` dispatches generic and SRVSVC levels. `libnet_RemoteTOD_generic()` maps generic input to the SRVSVC backend. `libnet_RemoteTOD_srvsvc()` connects to the server's SRVSVC pipe, calls `srvsvc_NetRemoteTOD`, converts `srvsvc_NetRemoteTODInfo` fields into `time_t` with `timegm()`, and returns timezone offset in seconds.

## Control Flow

The SRVSVC flow connects to `LIBNET_RPC_CONNECT_SERVER`, formats `server_unc`, calls the generated RPC stub, checks both NTSTATUS and WERROR, converts the returned broken-down remote time into UTC `time_t`, stores timezone minutes multiplied by 60, and frees the RPC pipe.

## State and Persistence Behavior

This is read-only. It allocates temporary RPC structures and returns scalar time values plus an error string. No local or remote persistent state is changed.

## Dependencies and Integration Points

The file depends on `libnet_RpcConnect`, generated SRVSVC client stubs, `timegm`, WERROR conversion, and the Python `net.time()` binding in `py_net.c`.

## Risks and Edge Cases

The UNC string uses `"\\%s"` rather than the double-backslash pattern used elsewhere, which may be intentional for the generated API or may deserve compatibility testing. The code trusts returned date fields enough to feed `timegm()`. Timezone sign semantics depend on SRVSVC's `timezone` convention and should be checked against Windows/Samba behavior.

## Test Signals

Useful tests compare returned time against the remote host clock within tolerance, validate timezone sign/units, cover transport and WERROR failures, and exercise Python `Net.time()`.

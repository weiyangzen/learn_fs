# sources/user-network-fs/samba/source3/torture/test_smbsock_any_connect.c

## Purpose

`test_smbsock_any_connect.c` provides a focused torture entry point for `smbsock_any_connect`, Samba's helper for attempting SMB connections across a list of candidate socket addresses and configured SMB transports. The test is intentionally tolerant: it prints the returned status but always returns `true`, so it acts more like a smoke/coverage probe than a strict connectivity assertion.

## Important APIs, Types, and Functions

- `run_smb_any_connect`: the sole exported torture test function.
- `struct sockaddr_storage addrs[5]`: fixed candidate address list populated with unroutable/test IPv4 addresses `192.168.99.5` through `192.168.99.9`.
- `struct smb_transports`: parsed transport configuration from `lp_client_smb_transports()`.
- `struct loadparm_context`: loadparm context created with `loadparm_init_s3`.
- `struct smbXcli_transport *xtp`: output transport returned by a successful connection.
- `smb_transports_parse`, `interpret_string_addr`, `smbsock_any_connect`, `nt_errstr`, and `TALLOC_FREE` are the key calls.

## Control Flow

The function initializes an s3 loadparm context, converts five string IP addresses into `sockaddr_storage` values, and calls `smbsock_any_connect` with the address array, no explicit names or socket options, the parsed client transport set, zero flags, and output pointers for the chosen transport and chosen address index. It frees the loadparm context immediately after the call, prints the resulting `NTSTATUS`, frees the returned transport only if the status is OK, and returns `true`.

There is only one hard failure path: if `loadparm_init_s3` returns `NULL`, the test returns `false`. Connection failure itself is not considered a failed torture result.

## State and Persistence Behavior

The test has no filesystem persistence. Runtime state is limited to stack-allocated socket addresses, the temporary loadparm context, parsed transport configuration, and a possible talloc-owned `smbXcli_transport`. The selected address index is captured but not inspected.

## Dependencies and Integration Points

The file depends on Samba parameter/loading code (`lib/param/param.h`, `source3/param/loadparm.h`), the socket connection helper (`libsmb/smbsock_connect.h`), and torture registration declarations (`torture/proto.h`). It consumes global Samba client transport configuration via `lp_client_smb_transports`.

Because the addresses are fixed, the observed status depends on the worker host network, routing, firewall behavior, and configured SMB transports. The current implementation is designed not to fail the test suite merely because the addresses are unreachable.

## Risks and Edge Cases

- Since the result is always success after initialization, regressions in failure status selection, timeout behavior, or chosen-index semantics may only be visible in logs.
- If any of the nominally test-only addresses become reachable in a local environment, the test will allocate and then free a live transport, but it still does not verify that the chosen index or transport matches expectations.
- The parsed transport configuration is passed by address from a stack variable; this is fine for the synchronous call but would be unsafe if future connection code retained it beyond the call.

## Test Signals

The primary signal is the printed line `smbsock_any_connect returned <status>`. A strict failure only indicates loadparm initialization failure. Useful manual signals include whether the status is a reasonable connection failure for unreachable addresses and whether a successful connection path frees `xtp` without leaks or crashes.

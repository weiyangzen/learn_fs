# File Research: sources/virtualization/nbd/tests/run/simple_test

## Purpose
POSIX shell integration-test harness that creates temporary NBD server configurations, starts `nbd-server`, runs client/test scenarios, and cleans up.

## Main Scenarios
Covers:
- single and multiple configured exports
- oversized requests
- write tests
- treefile and readonly treefile exports
- flush/FUA/rotational flags
- included config directories
- integrity and large-integrity transaction traces
- export listing through `nbd-client`
- readonly write failure expectations
- Unix-domain sockets
- inetd mode
- handshake error handling
- TLS success, huge TLS transfer, and wrong-certificate failure
- netlink connection-status checks with `libnl_mock.so`
- netlink connect/disconnect behavior
- persist mode and dead-connection timeout options

## Control Flow
The script creates a temporary directory, config file, PID file, and backing image. Each `case` arm writes a minimal config, starts `../../nbd-server` when needed, waits briefly, runs `nbd-tester-client` or `nbd-client`, and stores `retval`. Cleanup kills the daemon by PID file or background PID and removes the temp directory unless requested otherwise.

## Dependencies
Requires POSIX shell tools, `dd`, `mktemp`, `realpath` or `readlink -f`, built `nbd-server`, `nbd-client`, `nbd-tester-client`, optional TLS cert fixtures, optional `timeout`, and optional `libnl_mock.so`.

## Risks and Notes
The harness uses a fixed default delay of one second before connecting, which may be timing-sensitive on slow systems. Some Linux-only checks return skip code `77`. The script intentionally accepts expected failures in readonly/TLS-wrong-cert/netlink cases.

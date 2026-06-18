# sources/user-network-fs/samba/source4/lib/socket/testsuite.c

## Purpose

`testsuite.c` provides local torture tests for the source4 socket abstraction. It validates basic UDP datagram behavior and TCP stream behavior over the `"ip"` backend on the best loopback interface address.

## Important APIs, Types, and Functions

`test_udp()` creates two datagram sockets, binds one, sends random data both directions with `socket_sendto()`/`socket_recvfrom()`, and checks addresses, ports, sizes, and bytes. `test_tcp()` creates a listener/client pair, connects with `socket_connect_ev()`, accepts, sends random bytes, receives them, and validates peer address and payload. `torture_local_socket()` registers the `udp` and `tcp` tests.

## Control Flow

Both tests load interface data from loadparm, choose a loopback address through `iface_list_best_ip()`, create sockets, bind/listen on port zero, discover the assigned local address, and exercise one round-trip or one client-to-server transfer. Failures are reported through torture assertions.

## State and Persistence Behavior

The tests allocate all sockets and blobs under the torture context, relying on talloc cleanup. They bind ephemeral local ports only and do not persist files or network configuration.

## Dependencies and Integration Points

The file integrates with Samba torture local suites, tevent, loadparm, interface discovery, random buffer generation, and the async connect helper from the socket subsystem.

## Risks and Edge Cases

Coverage is intentionally basic. It does not test Unix-domain sockets, IPv6, error paths, partial nonblocking mode, socket options, fd duplication, address conversion helpers, or TLS/encrypted socket behavior. Loopback selection depends on local interface configuration.

## Test Signals

Passing `torture_local_socket` confirms basic IPv4-style UDP/TCP behavior. Regressions in bind, ephemeral port discovery, send/recv byte accounting, or async TCP connect should show up here.

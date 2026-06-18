# sources/user-network-fs/samba/source4/lib/socket/connect_multi.c

## Purpose

`connect_multi.c` races nonblocking connect attempts across all resolved addresses and multiple ports, returning the first successful socket or the last completion error. It can also run an optional post-connect establishment handshake before accepting a connection.

## Important APIs, Types, and Functions

`struct connect_multi_state` tracks resolved addresses, ports, current address/port cursor, sent/received attempt counts, winning socket/port, and optional `socket_connect_multi_ex` hooks. `struct connect_one_state` stores a single attempt's composite, socket, and address. Public APIs include `socket_connect_multi_ex_send()`, `socket_connect_multi_ex_recv()`, `socket_connect_multi_ex()`, `socket_connect_multi_send()`, `socket_connect_multi_recv()`, and `socket_connect_multi()`.

## Control Flow

The send function copies the caller's port list, starts `resolve_name_all_send()` for the server name using the first port, and continues in `continue_resolve_name()`. After resolution, `connect_multi_next_socket()` creates one socket for the current address/port, starts `socket_connect_send()`, advances the cursor, and sets a short timer to launch the next attempt even before the current one finishes. `continue_one()` receives a connect result; without hooks, a successful connect steals the socket and completes the composite, while failure triggers more attempts until all are received. With hooks, successful or failed raw connect completion is followed by `ex->establish_send()` and `continue_one_ex()` uses `establish_recv()` as the acceptance result.

## State and Persistence Behavior

All attempt state is talloc-owned by the composite. Timers are children of individual attempt state, so they vanish when that attempt state is freed. The winning socket is stolen to the caller in recv. Failed sockets and states are freed as attempts complete.

## Dependencies and Integration Points

It depends on name resolution (`resolve_name_all_send/recv`), Samba socket creation/connect wrappers, tevent timers, and composite async control. Higher-level SMB or RPC clients can use it to try NetBIOS/SMB ports or perform transport-specific establishment checks.

## Risks and Edge Cases

`MULTI_PORT_DELAY` is documented as microseconds and set to 2000, but comments say a couple of milliseconds; aggressive racing can create many simultaneous attempts for many addresses/ports. In `continue_one()`, the optional `ex` handshake is invoked regardless of raw connect `status`, so the hook must tolerate failed sockets or this path may be wrong. The final returned error is whichever attempt completes last, not necessarily the most informative. No explicit global timeout is provided here.

## Test Signals

Tests should simulate multiple addresses and ports with controlled success/failure ordering, verify the first successful port is returned, ensure all-fail returns an error after every attempt completes, cover DNS failure, check timer fan-out, and exercise `socket_connect_multi_ex` hooks for both accepted and rejected handshakes.

Source-read signal: reviewed complete local file (392 lines).

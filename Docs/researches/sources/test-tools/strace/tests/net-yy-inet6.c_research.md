# sources/test-tools/strace/tests/net-yy-inet6.c

Purpose: builds the IPv6 version of the `net-yy-inet.c` test by defining address-family, field, loopback, and formatting macros before including the shared implementation.

Important APIs, types, and helpers: inherits the TCP lifecycle from `net-yy-inet.c` with `AF_INET6`, `struct sockaddr_in6`, `IN6ADDR_LOOPBACK_INIT`, `sin6_port`, `TCPv6`, and IPv6 address formatting fields.

Control flow: local source has no runtime body beyond macro definitions. The included implementation binds `::1`, connects a TCPv6 client, accepts, transfers data, and checks `-yy` fd endpoint output.

State and persistence: uses only ephemeral IPv6 loopback sockets and dynamic ports. No files or long-lived kernel objects are persisted.

Dependencies and integration points: depends on IPv6 loopback support, TCPv6, `/proc/self/fd/`, and the shared test body’s macro contract. It is sensitive to systems where IPv6 is disabled.

Risks and edge cases: macro mismatch would corrupt expected field names; missing IPv6 support should produce a skip/failure depending on harness behavior. Scope-id formatting must remain stable as `SA_FIELDS` is set to `sin6_scope_id=0`.

Test signals: same as the IPv4 shared test, but annotations and sockaddr text should use `[::1]`, `AF_INET6`, `TCPv6`, and IPv6-specific fields.

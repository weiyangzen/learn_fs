# sources/object-store/openstack-swift/swift/common/utils/ipaddrs.py

## Purpose

`ipaddrs.py` provides IP address validation, IPv6 normalization, local interface address discovery, and host/port parsing for Swift service and middleware configuration. It is split out so network-address helpers can be reused without importing the full `swift.common.utils` compatibility module.

## Important APIs, Types, And Functions

- `IPV6_RE` validates bracketed IPv6 host literals with an optional port.
- `is_valid_ip()`, `is_valid_ipv4()`, and `is_valid_ipv6()` validate textual addresses using `socket.inet_pton`.
- `expand_ipv6(address)` round-trips through `inet_pton`/`inet_ntop` to normalize a valid IPv6 address.
- `errcheck()` is a ctypes error checker for `getifaddrs`.
- ctypes structures `sockaddr_in4`, `sockaddr_in6`, and `ifaddrs` model the subset of libc interface-address structures Swift needs, with Linux versus BSD/macOS field layouts.
- `whataremyips(ring_ip=None)` returns the service's relevant IPs, either a specific configured bind/ring IP or all local interface IPv4/IPv6 addresses when binding to wildcard addresses.
- `parse_socket_string(socket_string, default_port)` parses DNS names, IPv4 addresses, or bracketed IPv6 literals with optional port into `(host, port)`.

## Control Flow And Behavior

Import-time code loads libc with `use_errno=True`, binds `getifaddrs` and `freeifaddrs`, and installs `errcheck()` on `getifaddrs`. Structure definitions switch on `platform.system()` so Linux uses 16-bit address-family fields while BSD/macOS include leading length bytes.

`whataremyips()` first handles a configured `ring_ip`. If it can be resolved as a numeric host and is not `0.0.0.0` or `::`, it returns that value directly. Otherwise, it calls `getifaddrs()`, iterates the linked list, skips entries without addresses, converts IPv4 and IPv6 addresses with `inet_ntop`, and frees the linked list in a `finally` block.

`parse_socket_string()` defaults the port, requires IPv6 literals to start with `[`, applies `IPV6_RE` to bracketed hosts, rejects unbracketed strings with more than one colon as ambiguous IPv6, and otherwise splits `host:port` or returns the bare host with default port.

## State And Persistence

The module holds process-global ctypes handles for libc functions. It reads kernel/network interface state through `getifaddrs()` but does not persist anything.

## Dependencies And Integration Points

Dependencies are `ctypes`, `ctypes.util`, `os`, `platform`, `re`, and `socket`. `__init__.py` re-exports the public helpers. `whataremyips()` is used by storage policy, account/container services, replicators, reconstructors, reapers, sharder, and sync code to decide local-device ownership and bind/listen identity. `parse_socket_string()` is used by memcached and cname lookup configuration parsing. Validation helpers are used by rsync formatting and network option handling.

## Risks And Edge Cases

- `errcheck()` calls `ctypes.set_errno(0)` rather than `ctypes.get_errno()`, which appears unusual for reporting the actual libc errno.
- ctypes structure layouts must match platform ABI. The module assumes any non-Linux platform is BSD/macOS-like.
- `whataremyips()` returns the configured `ring_ip` directly when it is specific, even if that value is a hostname rather than an IP after `getaddrinfo()` failure.
- The returned address list may include duplicates, loopback addresses, IPv6 link-local addresses, and interface-order-dependent values.
- `parse_socket_string()` returns `port` as whatever string/default was provided; it does not coerce to int or validate port range.
- Bracketed IPv6 parsing validates bracket syntax but does not call `is_valid_ipv6()` on the captured address.

## Test Signals

No local test tree is present. Expected coverage should mock `socket.inet_pton`, `socket.getaddrinfo`, and `getifaddrs()` linked-list data; validate IPv4/IPv6 positive and negative cases; verify wildcard versus specific `ring_ip` behavior; confirm `freeifaddrs()` is called on success and error; and exercise `parse_socket_string()` for hostnames, IPv4 with port, bracketed IPv6 with and without port, unbracketed IPv6 rejection, and default-port preservation.

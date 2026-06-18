# sources/user-network-fs/nfs-ganesha/src/support/ip_utils.c

## Purpose
`ip_utils.c` provides address and CIDR utilities for Ganesha support code. It hashes, displays, parses, compares, and canonicalizes socket addresses; detects loopback and wildcard addresses; and implements a local replacement for the subset of libcidr behavior used by export/client matching and DBus compatibility.

## Important APIs, Types, And Functions
Socket-address helpers:

- `hash_sockaddr()` hashes IPv4, IPv6, and optionally VSOCK addresses, with optional port exclusion. IPv4 is hashed as IPv4-mapped IPv6 for consistency.
- `display_sockaddr_port()` formats IPv4, IPv6, VSOCK, and local Unix addresses into a `display_buffer`.
- `ip_str_to_sockaddr()` parses IPv4 or IPv6 strings into `sockaddr_t`.
- `sockaddr_cmp()` canonicalizes IPv4 addresses to IPv4-mapped IPv6 before comparing address and optionally port. It also supports VSOCK when compiled.
- `get_port()` extracts IPv4, IPv6, or VSOCK port values.
- `convert_ipv6_to_ipv4()` recognizes IPv4-mapped IPv6 addresses and writes canonical IPv4.
- `ipv4_to_ipv4_mapped_ipv6()` maps IPv4 into IPv6 form.
- `is_loopback()` and `is_inaddrany()` handle IPv4, IPv6, and IPv4-mapped IPv6 forms.

CIDR helpers:

- `cidr_alloc()` and `cidr_free()` allocate/free `CIDR`.
- `cidr_from_str()` parses `address[/mask]`, validates mask bounds, and defaults to /32 or /128.
- `cidr_to_str()` renders address plus prefix length.
- `cidr_contains_ip()` tests whether an address is inside a CIDR network.
- `cidr_from_inaddr()` and `cidr_from_in6addr()` build host CIDRs.
- `cidr_ipaddr_to_chars()` and `cidr_mask_to_chars()` provide legacy 16-byte array forms formerly supplied by libcidr.
- `cidr_family()`, `cidr_proto()`, and `cidr_version()` expose compatibility metadata.
- `cidr_equals()` compares CIDR objects.
- `normalize_v4_mapped_cidr()` converts IPv4-mapped IPv6 CIDRs into canonical IPv4 and adjusts masks.

## Control Flow
Address parsing first tries `inet_pton(AF_INET)`, then `inet_pton(AF_INET6)`. Comparisons map IPv4 inputs to IPv4-mapped IPv6 so mixed IPv4/IPv6 forms sort consistently. Display uses `inet_ntop()` for IP families and writes either `addr` or `addr:port`.

CIDR parsing copies the input into a bounded buffer, splits on `/`, parses the address with `ip_str_to_sockaddr()`, validates a numeric mask if present, or assigns host masks by family. Containment checks require matching address family, then compare full bytes and remaining prefix bits for IPv6 or shifted host-order integers for IPv4. Normalization is explicit; callers must invoke `normalize_v4_mapped_cidr()` before CIDR comparisons if they want mapped IPv6 to behave as IPv4.

## State And Persistence Behavior
The module has almost no mutable global state. `ten_bytes_all_0` is a static zero-filled prefix used to recognize IPv4-mapped IPv6 addresses. All CIDR objects are heap allocated through Ganesha memory helpers and owned by callers. Functions set `errno` to `EINVAL` or `ENAMETOOLONG` on parse/validation failures in CIDR paths and generally return negative comparator or error values for unsupported families.

## Dependencies And Integration Points
The file uses libc networking APIs (`inet_pton`, `inet_ntop`, byte-order helpers), Unix socket structures, optional Linux VSOCK support, Ganesha `display_buffer`, logging, and memory helpers. It integrates with export/client matching, DBus export display compatibility, logging, and any subsystem comparing caller or server socket addresses.

## Risks And Edge Cases
The IPv6 branch in `ip_str_to_sockaddr()` temporarily sets `sp->ss_family = AF_INET` before calling `convert_ipv6_to_ipv4()`, whose conversion check requires `AF_INET6`. As written, IPv4-mapped IPv6 strings may not canonicalize to IPv4 in that path and should be tested.

The `AF_VSOCK` case in `display_sockaddr_port()` uses a string format for `svm_cid` even though the value is numeric. Builds with `RPC_VSOCK` should review this format string.

`cidr_mask_to_chars()` writes `chars[i]` after the full-byte loop even when `mask_bits == 0`. For `/32` IPv4 and `/128` IPv6, `i` can be 16, which is outside the documented 16-byte output buffer.

`cidr_contains_ip()` uses signed `int` for host-order IPv4 values. Networks with the high bit set can be affected by implementation-defined right shifts. `uint32_t` would be safer.

`cidr_equals()` requires exact socket-address equality after family and mask checks. Its comment describes network equivalence, but the implementation does not ignore host bits within the mask. For example, two separately constructed `/24` CIDRs with different host bits will not compare equal.

`cidr_contains_ip()` rejects family mismatches, so callers must normalize IPv4-mapped IPv6 CIDRs and addresses before containment checks when mixed representations are possible.

## Test Signals
High-value tests include IPv4, IPv6, IPv4-mapped IPv6 parsing and normalization; loopback and wildcard detection for native and mapped forms; `sockaddr_cmp()` with and without ports; hash equality expectations for IPv4 versus mapped IPv6; CIDR parsing with invalid masks and long strings; containment for `/0`, `/1`, `/31`, `/32`, `/127`, and `/128`; legacy char-array output bounds under ASAN; VSOCK formatting when enabled; and `cidr_equals()` behavior for same-network but different-host inputs.

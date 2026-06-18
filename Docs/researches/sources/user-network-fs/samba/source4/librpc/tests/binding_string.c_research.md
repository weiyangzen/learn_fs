# sources/user-network-fs/samba/source4/librpc/tests/binding_string.c

## Purpose

`binding_string.c` is a local torture test suite for DCE/RPC binding string parsing, formatting, protocol tower conversion, options, flags, object UUIDs, and IPv6/address-only forms.

## Important APIs, Types, and Functions

The suite registers through `torture_local_binding_string()`. `test_BindingString()` performs parse/stringify/tower round trips for `test_strings[]`. `test_parse_check_results()` validates specific parsed fields, flags, host/target/principal/localaddress options, object UUID behavior, and association group IDs. `test_no_transport()` validates address strings parsed with `NCA_UNKNOWN` transport using `test_no_strings[]`.

## Control Flow

For each binding string, the test parses with `dcerpc_parse_binding()`, regenerates with `dcerpc_binding_string()`, builds an EPM tower, reconstructs a binding from that tower, restores the object UUID lost by tower conversion, strips non-endpoint options for tower comparison, and compares expected strings. The focused parse test runs targeted assertions for transport, endpoint, flags, object, abstract syntax, and string output.

## State and Persistence Behavior

The tests are memory-only and use the torture context as talloc parent. They do not require network I/O or persistent state.

## Dependencies and Integration Points

Dependencies include DCE/RPC binding/tower helpers, EPM tower structures, torture local framework, and IP address utilities. The suite is an important regression guard for the binding parser used by transport connection, endpoint mapping, auth, and Python connection paths.

## Risks and Test Signals

Risks include brittle string ordering expectations, partial tower comparison only for IPv4 host cases, and parser behavior around IPv6 colons, scope IDs, empty endpoints, and options. Test signals are failures in local torture `binding` tests after parser/formatter changes, especially for `target_hostname`, `target_principal`, `assoc_group_id`, no-transport address parsing, and sign/seal/connect/packet flags.

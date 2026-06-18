<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/famtab.h -->
# sources/security-integrity/audit-userspace/auparse/famtab.h

## Purpose
Maps Linux address-family constants to short audit strings for socket-domain and sockaddr interpretation.

## Important APIs, types, and functions
The file is an `_S(value, "name")` include table consumed by generated lookup helpers such as `fam_i2s`. It covers common families from `AF_LOCAL`, `AF_INET`, and `AF_INET6` through newer numeric entries such as `vsock`, `xdp`, and `mctp`.

## Control flow
No runtime control flow lives here. `interpret.c` includes the generated family lookup and calls it from `print_socket_domain` and `print_sockaddr`.

## State and persistence behavior
Static compile-time data only; no mutable or persistent state.

## Dependencies and integration points
Values come from Linux socket headers. Integration is through `gen_tables` generated lookup code and auparse field types for socket domains and sockaddr families.

## Risks and test signals
Risk is kernel header drift or missing families causing `unknown-family(...)` output. Tests should exercise known IPv4/IPv6/local/netlink values and at least one unknown numeric family.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/famtab.h -->

# File Research: sources/os/linux/linux-stable/fs/smb/client/dns_resolve.c

This file implements hostname-to-IP resolution for CIFS/SMB DFS and reconnect paths using the kernel DNS resolver upcall.

Main responsibilities:
- `dns_resolve_name()` validates input, recognizes literal IPv4/IPv6 addresses without upcall, optionally expands NetBIOS names with a DNS domain, then resolves via `dns_query()`.
- `resolve_name()` performs the DNS resolver query in the current task network namespace and converts the returned string address into a `sockaddr`.

Important behavior:
- Literal IP addresses skip the DNS upcall and return success if `cifs_convert_address()` accepts them.
- If a DNS domain is supplied and the name looks like a NetBIOS name, the resolver first tries `<name>.<domain>`.
- If FQDN resolution fails, it falls back to resolving the original name.
- Failed conversion after a resolver result becomes `-EHOSTUNREACH`.

External dependencies:
- Uses `dns_query()` from the kernel DNS resolver.
- Uses CIFS address parsing and NetBIOS-name helpers from `cifsproto.h`.

Research notes:
- The helper is namespace-aware through `current->nsproxy->net_ns`.
- It is used by DFS target parsing, reconnect hostname refresh, and target/share matching.

# File Research: sources/os/linux/linux/fs/smb/client/dns_resolve.h

## Purpose
Declares CIFS DNS resolver helpers for hostname and UNC resolution.

## Main Contents
- Declares `dns_resolve_name()`.
- Defines inline `dns_resolve_unc()`, which extracts the hostname from a UNC path and resolves it.

## Integration Points
Included by DFS cache, DFS mount, and connection reconnect code. `dns_resolve_unc()` depends on `extract_unc_hostname()` to parse the server component from a UNC string before delegating to `dns_resolve_name()`.

## Risks And Review Focus
- `dns_resolve_unc()` rejects UNC strings shorter than three characters or without a hostname.
- Callers must pass a writable `struct sockaddr` storage area large enough for IPv4 or IPv6 results.

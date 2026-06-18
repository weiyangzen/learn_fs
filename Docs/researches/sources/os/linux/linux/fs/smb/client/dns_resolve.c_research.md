# File Research: sources/os/linux/linux/fs/smb/client/dns_resolve.c

## Purpose
Implements CIFS DNS resolver upcalls for converting SMB/DFS hostnames to socket addresses.

## Main Interfaces
- `dns_resolve_name()` resolves a hostname or address string into `struct sockaddr`.

## Control Flow
`dns_resolve_name()` first validates inputs and tries `cifs_convert_address()` so numeric IPv4/IPv6 addresses skip DNS upcall. If the name appears to be NetBIOS-style and a DNS domain is supplied, it constructs `name.domain` and tries that first. If that fails or does not apply, it calls `resolve_name()` on the original name.

`resolve_name()` uses `dns_query()` in the current network namespace, then converts the returned string IP address into a socket address with `cifs_convert_address()`.

## State And Synchronization
The file is stateless. It allocates temporary strings for FQDN construction and for the DNS resolver result, freeing both before return.

## Integration Points
- Used by DFS mount/referral logic and reconnect hostname refresh.
- Depends on the kernel DNS resolver key/upcall infrastructure.
- Uses CIFS address parsing and NetBIOS-name helpers from `cifsproto.h`.

## Risks And Review Focus
- DNS upcall failures propagate as negative errno values and can affect DFS mount/reconnect failover.
- FQDN construction length is bounded by `CIFS_MAX_DOMAINNAME_LEN`; changes to domain handling should preserve this bound.
- The function treats failed numeric conversion as a signal to try DNS, but failed DNS result is terminal.

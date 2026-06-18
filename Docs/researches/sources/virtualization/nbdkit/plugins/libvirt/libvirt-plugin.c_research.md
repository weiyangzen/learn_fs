# File Research: sources/virtualization/nbdkit/plugins/libvirt/libvirt-plugin.c

This read-only plugin exposes a libvirt guest disk using `virDomainBlockPeek`.

Configuration:
- `domain` is required.
- `disk` is required.
- `connect` optionally sets a libvirt URI.

Connection setup:
- Opens a libvirt connection with `virConnectOpen`.
- Looks up the domain by name.
- Gets block info for the named disk and uses `info.physical` as export size.

I/O:
- Thread model serializes requests.
- `.pread` loops until the request is served.
- Individual `virDomainBlockPeek` calls are capped at 1 MiB for compatibility with older libvirt limits.
- Read failures set `errno = EIO`.

Limitations:
- Read-only by design because libvirt has no equivalent write API here.
- Uses libvirt error output indirectly; nbdkit messages point to earlier libvirt errors.

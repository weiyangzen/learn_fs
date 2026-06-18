# File Research: sources/os/bsd/netbsd-src/lib/libwrap/hosts_access.c

## Purpose
Implements TCP wrappers host access control using `/etc/hosts.allow` and `/etc/hosts.deny`.

## Key Details
- `hosts_access` checks allow table first, then deny table, defaulting to allow.
- On deny/error, notifies `blocklist`.
- `table_match` reads logical lines, skips comments/blank lines, splits daemon/client/command fields, and optionally executes matched command/options.
- `list_match` supports comma/space-separated patterns and `EXCEPT`.
- Server patterns can be daemon or `daemon@host`.
- Client patterns can be host or `user@host`.
- Host matching supports netgroups, file-backed pattern lists, `KNOWN`, `LOCAL`, RBL lookups, net/mask expressions, exact/prefix/suffix names, and addresses.
- IPv4 matching requires dotted-quad forms.
- IPv6 matching supports numeric masks or prefix lengths and IPv4-mapped address special handling when compiled with `INET6`.

## Dependencies and Role
- Core access-control engine for `libwrap`.

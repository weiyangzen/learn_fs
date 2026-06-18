# File Research: sources/os/plan9/plan9/sys/src/9/ip/nullmedium.c

Defines a placeholder `null` IP medium.

Key behavior:
- `nullbind` always errors with `cannot bind null device`.
- `nullunbind` is a no-op.
- `nullbwrite` errors with `nullbwrite`.
- `nullmediumlink` registers the medium.

Notable use:
- Installed during IP device reset as a known medium name, but it is intentionally nonfunctional.

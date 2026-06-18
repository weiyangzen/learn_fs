# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libip/classmask.c

Computes default IP network masks.

Key functions/data:
- `classmask`: default classful IPv4 masks stored in IPv6-mapped form.
- IPv6 special masks for loopback, link-local, multicast, and solicited-node multicast.
- `defmask`: returns an appropriate default mask for IPv4-mapped or IPv6 addresses.
- `maskip`: applies a mask bytewise.

Important behavior:
- IPv4 detection depends on `isv4`.
- IPv6 defaults are prefix based, with all-bits mask as the fallback.

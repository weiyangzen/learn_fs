# File Research: sources/virtualization/nbdkit/server/uri.c

This file builds the debug/display NBD URI for the current service mode. Socket activation and stdin modes cannot be represented and return `NULL`. TCP, Unix socket, and vsock modes choose `nbd`, `nbds`, `nbd+unix`, `nbds+unix`, `nbd+vsock`, or `nbds+vsock` depending on whether TLS is required.

The URI is assembled with `open_memstream` and `uri_quote`. Unix socket mode encodes the socket path as `?socket=...` and puts a non-empty export name in the path. TCP mode uses `localhost` plus optional port and export name. Vsock mode uses CID `1` (`VMADDR_CID_LOCAL`) plus optional port and export name.

When TLS is required and certificate or PSK configuration is present, it appends `tls-certificates=` or `tls-psk-file=` query parameters. Comments note client compatibility caveats, including older libnbd and qemu behavior. The result is logged through debug output.

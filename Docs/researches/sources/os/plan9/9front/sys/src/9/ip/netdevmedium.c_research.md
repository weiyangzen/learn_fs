# File Research: sources/os/plan9/9front/sys/src/9/ip/netdevmedium.c

Implements a generic network-device-backed IP medium.

Key elements:
- Binds an IP interface to an already-openable device path.
- Stores the device channel and reader process in `Netdevrock`.
- Starts a `netdevread` kernel process to read blocks from the device and inject them into IP input.
- Writes outbound packets through the underlying device’s `bwrite`.
- Unbinds by posting a note to the reader and waiting for it to exit.

Dependencies:
- Uses `namec`, `devtab` `bread`/`bwrite`, and `mediumunbindifc`.

Research notes:
- `unbindonclose` is false, so the medium is not automatically detached merely by closing a conversation.
- Reader death triggers interface unbind unless another unbind is already in progress.

# File Research: sources/os/linux/linux/io_uring/net.h

Networking header for io_uring.

Key contents:
- Defines `struct io_async_msghdr`, including cached vector storage and a `clear` group covering msghdr, sockaddr, payload/control metadata, and fast iovec.
- Declares all network prep/issue/cleanup functions when `CONFIG_NET` is enabled.
- Provides no-op stubs for cache cleanup and socket BPF population when networking is disabled.

This header is central to opcode table registration and request async-data sizing for network operations.

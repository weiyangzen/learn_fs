# File Research: sources/virtualization/nbd/man/nbd-client.8.sgml.in

DocBook manpage template for `nbd-client(8)`.

It documents connecting a Linux NBD device to an `nbd-server` export over TCP or Unix domain sockets, config lookup through `nbdtab`, disconnect, connection check, export listing, netlink usage, and version/help modes.

Documented options include block size, multiple connections, timeout, named export, check/disconnect/list, netlink disablement, backend identifier, persist, preinit, read-only, forced size, swap, systemd mark, nofork, no-optgo, Unix socket mode, and TLS files/hostname/priority.

The TLS section explains the userspace proxy design: `nbd-client` upgrades the network socket with STARTTLS, creates a socketpair, hands one side to the kernel, and runs an encrypt/decrypt proxy on the other. It also explains why TLS plus swap can reintroduce memory-pressure deadlocks because the PF_MEMALLOC behavior applies to the kernel-facing socket rather than the actual network socket.

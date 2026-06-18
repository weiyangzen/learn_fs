# File Research: sources/virtualization/nbd/nbd-client.c

Main implementation of `nbd-client`.

It includes client configuration globals, nbdtab parser callbacks, optional libnl netlink integration, TCP and Unix socket connection logic, newstyle negotiation, STARTTLS upgrade, export listing, kernel device setup, disconnect/check operations, and main process lifecycle.

The nbdtab callbacks populate `CLIENT` fields from parsed properties/flags and select the matching config row by device name. `get_from_config()` opens `SYSCONFDIR/nbdtab`, runs the generated parser, and validates that a matching row was found.

Netlink support can connect, disconnect, query status, and configure sockets through the kernel NBD generic netlink family. It sends size, block size, server flags, timeout, dead connection timeout, optional backend identifier, and socket FDs. Netlink mode skips the old daemon path.

Connection setup supports TCP via `getaddrinfo()` and Unix domain sockets. Negotiation reads `NBDMAGIC`, option magic, global flags, sends client flags, optionally upgrades with `NBD_OPT_STARTTLS`, handles `NBD_OPT_LIST`, prefers `NBD_OPT_GO`, and falls back to `NBD_OPT_EXPORT_NAME` on unsupported GO/INFO replies.

TLS support creates a socketpair and forks a proxy process running `tlssession_mainloop()`, then uses the plaintext socket for NBD traffic handed to the kernel.

The ioctl path opens the NBD device, sets size/block size, flags, read-only state, timeout, socket FDs, optional swap memory behavior, daemonizes unless suppressed, forks a helper to trigger partition reread, runs `NBD_DO_IT`, clears sockets on exit, and supports reconnect loops in persist mode.

Newer persist-related netlink code includes multicast monitoring and reconnect/reconfigure helpers, but the callback currently only logs link-dead messages and contains TODO-level device matching/reconnect integration.

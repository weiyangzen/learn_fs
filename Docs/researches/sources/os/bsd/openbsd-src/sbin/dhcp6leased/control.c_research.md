# File Research: sources/os/bsd/openbsd-src/sbin/dhcp6leased/control.c

Control socket handling for `dhcp6leased`.

It creates a nonblocking Unix-domain control socket, unlinks any stale path, binds with restrictive permissions, chmods the socket group-readable/writable, listens, and accepts client connections into per-client imsg buffers. Descriptor exhaustion pauses accepting briefly with an event timer to avoid a tight failure loop.

Accepted control imsgs support reload, verbosity changes, interface-info requests, and explicit DHCP request/reboot triggers. Requests are forwarded to the main or engine process as appropriate, verbosity changes also update the frontend’s local log level, and responses are relayed back to the originating control connection by matching imsg pid.

# File Research: sources/os/bsd/openbsd-src/sbin/iked/control.c

`control.c` implements the Unix-domain control socket process used by `ikectl`-style clients. It creates/listens on the control socket, accepts nonblocking connections, tracks connected clients with per-connection peer IDs, and forwards control imsgs to parent, IKEv2, or CA.

The control process supports notify subscriptions, verbosity changes, reload/reset/couple/decouple/active/passive commands, reset-by-ID, show-SA, show-stats, and show-certstore requests. Replies are routed back by peer ID so command responses reach the requesting client.

It handles file-descriptor pressure by pausing accept on `ENFILE`/`EMFILE` and resuming with a timer. Socket permissions differ for restricted vs nonrestricted sockets. Runtime pledge is limited to stdio, unix, and recvfd.

Important coupling: parent handles reload/reset/mode control, IKEv2 handles SA/stats/reset-ID views, and CA handles certificate-store display. Notify clients receive forwarded imsgs broadcast from control traffic.

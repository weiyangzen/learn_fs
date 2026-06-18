# File Research: sources/os/bsd/openbsd-src/sbin/unwind/unwind.h

This is the shared internal header for `unwind`. It defines paths, option bits, resolver type enums, imsg types, config structures, and cross-module function prototypes.

Key contents:
- Runtime paths: `/etc/unwind.conf`, `/dev/unwind.sock`, daemon user `_unwind`.
- DNSSEC root trust anchor constants for KSK2017 and KSK2024.
- Resolver types: recursor, autoconf, oDoT autoconf, ASR stub, forwarder, oDoT forwarder, DoT.
- `struct imsgev`: imsg buffer plus libevent state.
- `enum imsg_type`: all control/config/socket/query/status messages used between processes.
- `struct uw_forwarder`, `struct force_tree_entry`, `struct resolver_preference`, `struct uw_conf`.
- Query/answer wire structs for resolver/frontend communication.

Filesystem/OS relevance:
- Captures the daemon’s internal control protocol and config ownership model.
- Uses OpenBSD queue/tree primitives and imsg/event APIs.

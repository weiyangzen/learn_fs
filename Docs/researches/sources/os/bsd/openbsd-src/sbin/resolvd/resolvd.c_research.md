# File Research: sources/os/bsd/openbsd-src/sbin/resolvd/resolvd.c

## Purpose

Daemon that listens for routing-socket DNS proposals and regenerates `/etc/resolv.conf`. It also integrates with `unwind` when available, preferring local resolver use while preserving proposed nameservers as commented fallback lines.

## Main State

`learned[ASR_MAXNS]` stores resolver proposals by interface index, address family, priority, and numeric IP string. `resolvfd` tracks the currently watched `/etc/resolv.conf`; `newkevent` rebuilds kqueue registrations. Non-small builds track whether `unwind` should be checked and whether its control socket is connected.

## Main Loop

`main()` parses debug/verbose flags, requires root, takes an exclusive nonblocking lock on `/dev/resolvd.lock`, daemonizes unless debugging, opens the route socket, filters for `RTM_PROPOSAL` and `RTM_IFANNOUNCE`, solicits current DNS proposals, unveils resolver files and optional unwind socket, pledges to `stdio unix rpath wpath cpath`, creates a kqueue, and enters an event loop.

Events include route socket readability, vnode changes on `/etc/resolv.conf`, and optional unwind socket readability/closure. Delete/rename of resolv.conf causes fd reset and regeneration; truncate/write causes a short sleep then regeneration to accommodate editors. Unwind connection changes also regenerate output.

## Route Message Handling

`route_receive()` reads one route message, validates basic length and version, ignores messages from itself, extracts sockaddr pointers with `get_rtaddrs()`, and calls `handle_route_message()`.

`handle_route_message()` copies current proposals into a local candidate array. Interface departure removes proposals from that interface. `RTM_PROPOSAL` with solicitation priority asks for a future unwind check. DNS proposals validate presence of `RTA_DNS`, address family, sockaddr length alignment, and count, then remove old proposals for the same interface/family and add new numeric IPv4/IPv6 nameserver strings. IPv6 link-local addresses get the route interface scope id before formatting. Proposals are sorted by priority with `mergesort()`, duplicate IPs per interface are zeroed, and a changed set triggers `regen_resolvconf()`.

## File Regeneration

`regen_resolvconf()` writes `/etc/resolv.conf.new`, building an iovec list. If unwind is running, it writes `nameserver 127.0.0.1`; learned nameservers are then emitted, commented out when unwind is active. It replays user-managed lines from the old `/etc/resolv.conf`, skipping lines containing the `# resolvd:` marker. It writes all data, fsyncs, renames into place, updates or replaces `resolvfd`, and asks the kqueue registration to be rebuilt. On error it closes the temp fd and unlinks the temp file.

## Logging

Non-small builds abstract console versus syslog logging through a `struct loggers` table. Debug mode logs to stderr; daemon mode logs through syslog. Verbose console logging is controlled by `-v`.

## Risks And Invariants

- `regen_resolvconf()` is all-or-nothing via temp file, fsync, and rename, but it preserves only user lines that fit within `UIO_MAXIOV` total iov entries.
- Lines containing `# resolvd: ` are considered daemon-managed and are not replayed.
- If proposal slots fill, `findslot()` discards the last slot for new proposals, assuming new data may be more important.
- Route-socket reads handle one buffer-sized message and reject partial messages; unusually large route messages beyond the fixed buffer are not processed.

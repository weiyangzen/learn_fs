# sources/user-network-fs/samba/source3/lib/addrchange.c

## Purpose
`addrchange.c` implements an asynchronous network-address change watcher for Samba. On Linux with rtnetlink support, it listens for IPv4/IPv6 address add/delete notifications and exposes them through a tevent request API. On non-rtnetlink builds, it returns unsupported/not-implemented stubs.

## Important APIs, Types, and Functions
- `struct addrchange_context`: owns a `tdgram_context` wrapping a netlink route socket.
- `addrchange_context_create`: allocates context, opens `AF_NETLINK`/`NETLINK_ROUTE`, sets close-on-exec, makes it nonblocking, binds to `RTMGRP_IPV6_IFADDR | RTMGRP_IPV4_IFADDR`, and wraps the socket with `tdgram_bsd_existing_socket`.
- `struct addrchange_state`: per-request state containing event context, context pointer, received buffer/from address, change type, parsed sockaddr, and interface index.
- `addrchange_send`: creates a tevent request and starts `tdgram_recvfrom_send`.
- `addrchange_done`: receives datagrams, validates netlink sender and message length/type, extracts `RTM_NEWADDR`/`RTM_DELADDR`, parses `ifaddrmsg` and `IFA_LOCAL`/`IFA_ADDRESS` attributes into IPv4/IPv6 `sockaddr_storage`, retries ignored messages, and completes the request.
- `addrchange_recv`: returns `ADDRCHANGE_ADD`/`ADDRCHANGE_DEL`, address, and optional ifindex.

## Control Flow and State
The Linux control flow is asynchronous. `addrchange_send` arms one receive operation. `addrchange_done` either completes the request with a parsed address change, maps errors to NTSTATUS, or loops by freeing stale receive buffers and starting another receive for irrelevant datagrams. It rejects messages not from kernel netlink pid 0, undersized messages, malformed lengths, and unexpected message types. The context is long-lived; each request handles one valid address-change event.

## Persistence Behavior
No persistent storage is used. State is in-memory talloc/tevent request state and the kernel netlink socket. The observed address changes are kernel network-interface state, not Samba-owned persistence.

## Dependencies and Integration Points
Linux path depends on `linux/netlink.h`, `linux/rtnetlink.h`, `tsocket/tdgram`, `tevent`, talloc, nonblocking socket helpers, and NTSTATUS/unix error mapping. Call sites include smbd server address-change handling, winbindd address-change handling, and `torture/test_addrchange.c`.

## Risks
- The current length calculation for netlink attributes is security-sensitive; malformed kernel or injected messages must not overrun parsing.
- The watcher is Linux-specific; non-Linux builds get no working events.
- Ignored messages trigger recursive re-arming from callback context; sustained irrelevant traffic could keep the request active indefinitely.
- It trusts kernel-origin netlink messages only after checking `nl_pid == 0`, which is an important spoofing guard.

## Test Signals
`run_addrchange` in source3 torture directly exercises the API. Additional signals include smbd/winbindd reacting to address add/delete events, Linux-only build coverage with `HAVE_LINUX_RTNETLINK_H`, non-Linux stub build coverage, malformed netlink message tests, and leak checks for repeated retry paths.

# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/bootp_subr.c

## Role

Implements kernel BOOTP/DHCP discovery for diskless NFS boot. It probes suitable network interfaces, temporarily configures them for broadcast discovery, accepts BOOTP/DHCP replies, decodes root/swap/hostname/network options, configures final interface state/routes, and obtains NFS root/swap file handles from mountd.

## Main Data Structures

- `struct bootp_packet` is the RFC951 packet format with large vendor option storage.
- `struct bootpc_ifcontext` tracks per-interface request/reply packets, socket, ifreq, link address, DHCP state, discovered IP/netmask/gateway/root flags, and DHCP server ID.
- `struct bootpc_tagcontext` accumulates DHCP option data and records malformed options or oversized tags.
- `struct bootpc_globalcontext` tracks all interfaces, global transaction IDs, root/swap/hostname selection, aggregate reply storage, and temporary option contexts.

## Major Entry Points

- `bootpc_init()` is the top-level diskless bootstrap routine.
- `bootpc_fakeup_interface()` brings candidate interfaces up and configures temporary address/netmask/broadcast state for discovery.
- `bootpc_compose_query()` builds BOOTP, DHCP Discover, or DHCP Request packets.
- `bootpc_call()` sends repeated broadcast requests and receives matching replies.
- `bootpc_received()` validates DHCP message transitions and decides whether a reply improves the current per-interface state.
- `bootpc_tag()` and `bootpc_tag_helper()` parse vendor options, including option-overload use of `file` and `sname`.
- `bootpc_decode_reply()` converts accepted replies into `nfsv3_diskless` root, swap, hostname, netmask, gateway, and mount option data.
- `bootpc_adjust_interface()` applies final interface addresses, broadcast address, netmask, and default route, or shuts failed interfaces down.
- Debug-only `bootpboot_p_*()` helpers print route and interface state.

## Implementation Notes

- DHCP is the default unless `BOOTP_NO_DHCP` is configured; code can fall back to BOOTP unless forced DHCP is configured.
- Each candidate interface receives a distinct transaction ID derived from a global base.
- The discovery socket is UDP broadcast with `SO_BROADCAST`, `SO_DONTROUTE`, and a one-second receive timeout.
- Replies are accepted only when the packet is long enough, is a BOOTP reply, matches the xid, matches hardware address length, and matches hardware address bytes.
- DHCP state advances from Discover to Offered to Request to Resolved; BOOTP replies may resolve directly.
- The send loop prefers interfaces with root paths and applies a settle delay once the needed root path is found.
- Option parser detects malformed tag lengths and concatenates repeated options up to `TAG_MAXLEN`.
- Recognized options include subnet mask, routers, hostname, root path, root options, swap path, swap options, swap size, DHCP message type/server/requested address/lease, and a site-specific cookie exported through `kern.bootp_cookie`.
- If no subnet mask is provided, classful defaults are used; if no gateway is provided, the client address is used for proxy ARP behavior.
- `bootpc_init()` calls `md_mount()` for root and optional swap, `md_lookup_swap()` for per-client swap lookup, and marks `nfs_diskless_valid = 3` after success.

## Dependencies

Uses DragonFly networking interfaces, sockets, routing, sysctl, NFS diskless structures, mountd RPC helpers, NFS mount option parsing, kernel RPC/XDR headers, and BOOTP/NFS-root compile options.

## Research Notes

This file is a full kernel network bootstrap path, not a normal NFS data path. It mutates interface state during early boot and treats missing root path as fatal only when BOOTP NFS root support requires it.

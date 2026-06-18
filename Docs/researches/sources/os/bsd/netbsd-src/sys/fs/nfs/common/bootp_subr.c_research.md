# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/bootp_subr.c

## Purpose
Implements kernel BOOTP/DHCP discovery for diskless NFS-root boot. It finds eligible network interfaces, temporarily configures them, sends BOOTP/DHCP packets, decodes replies, configures the selected interface, retrieves an NFS root file handle from mountd, and fills `nfsv3_diskless`.

## Main Data
- `struct bootp_packet` models RFC951 BOOTP packets with a large vendor/options area.
- `struct bootpc_ifcontext` stores per-interface query/reply packets, ifreq/in_aliasreq state, link address, IP/netmask/gateway, DHCP negotiation state, root-path flags, and MTU.
- `struct bootpc_tagcontext` stores decoded option data and parser error/overload state.
- `struct bootpc_globalcontext` tracks all interface contexts, global xid/time, root-path/hostname selection, current reply, and temporary option buffers.
- Global `bootp_cookie` stores site option 134 for sysctl/userland exposure; `bootp_so` is the UDP socket used for discovery.

## Key Flow
- `bootpc_init` exits if diskless config is already valid, allocates contexts, finds broadcast-capable Ethernet/FDDI/Token Ring interfaces or a `BOOTP_WIRED_TO` interface, creates a UDP socket, fakes interfaces up with `0.0.0.0/8`, composes queries, calls `bootpc_call`, decodes accepted replies, adjusts or shuts down interfaces, and optionally performs root mount discovery.
- `bootpc_compose_query` builds BOOTP or DHCP DISCOVER/REQUEST packets with RFC1048 cookie, maximum message size, vendor identifier, requested address/server ID, lease time, and broadcast flag.
- `bootpc_call` sets socket timeout/broadcast/dontroute, binds to client port 68, sends packets to broadcast server port 67, temporarily switches interface masks for sending, receives replies, matches xid/hardware address, accepts or ignores replies through `bootpc_received`, and handles retries/settle delays/timeouts.
- `bootpc_received` validates option parsing, enforces expected DHCP message type, stores better replies, advances DHCP state, and notes root path, router, netmask, and DHCP server ID availability.
- `bootpc_decode_reply` extracts assigned IP, server/gateway, subnet mask, routers, root path, root mount options, hostname, cookie, and MTU. It supports environment/rootdev overrides for NFS root.
- `bootpc_adjust_interface` installs final IP/netmask/broadcast/MTU on resolved interfaces; failed interfaces are shut down.
- `md_mount` uses `krpc_portmap` and `krpc_call` to talk to mountd, optionally tries NFSv3 first, falls back to v2, decodes mount reply file handle and auth flavors, and resolves the NFS service port.

## Helpers
Includes IPv4 parser helpers (`getip`, `getdec`), root path parser (`setmyfs`), NFS mount option defaults (`mountopts`), local XDR decode helpers, BOOTP option parsing with overload support, default route add/remove around mountd access, and optional BOOTP debug route/interface printers.

## Dependencies
Depends on kernel sockets, interface ioctl APIs, routing APIs, NFS diskless structures, NFS mount argument parsing, NFS protocol constants, and the small KRPC helper API in `krpc.h`/`krpc_subr.c`.

## Risks and Edge Cases
- Runs during early boot and uses `panic` for many unexpected interface/ioctl/parser failures.
- Only IPv4 BOOTP/DHCP is implemented.
- Option parsing supports overload and concatenated tags, but malformed options can invalidate replies.
- Interface manipulation is invasive: temporary addresses/masks/routes must be restored or adjusted correctly.
- Root selection has precedence interactions between server-provided root path, `vfs.root.mountfrom`, `ROOTDEVNAME`, and boot flags.

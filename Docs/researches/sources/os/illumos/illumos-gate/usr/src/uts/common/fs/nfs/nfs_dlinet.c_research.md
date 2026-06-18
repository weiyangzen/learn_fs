# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_dlinet.c

## Purpose

`nfs_dlinet.c` implements diskless boot networking and NFS root mounting support. It configures the boot network interface, discovers the client identity and root server through boot properties, DHCP, RARP, and bootparams, obtains NFS filehandles through the mount protocol, chooses UDP or TCP, and builds NFS mount arguments for root.

This file is built as a miscellaneous module named “Boot diskless” and exports the `mount_root()` entry used by `nfs_common.c`’s dynamic root mount path.

## Main Interfaces

Module entry points:

- `_init`
- `_fini`
- `_info`

Root mount and server discovery:

- `mount_root`
- `getfile`
- `mountnfs`
- `mountnfs3`
- `ping_prog`
- `init_mountopts`

Network/bootstrap configuration:

- `init_config`
- `bp_netconfig`
- `dhcpinit`
- `cacheinit`
- `cacheinfo`
- `whoami`
- `revarp_myaddr`
- `revarp_start`
- `revarpinput`
- `dlifconfig`
- `ifioctl`
- `rtioctl`
- `setifflags`

RPC/XDR helpers:

- `pmap_kgetport`
- `pmap_rmt_call`
- `mycallrpc`
- `myxdr_fhstatus`
- `myxdr_fhandle`
- `myxdr_mountres3`
- `myxdr_mountres3_ok`
- `myxdr_fhandle3`
- `myxdr_rmtcall_args`
- `myxdr_rmtcallres`
- `myxdr_pmap`

Utility helpers:

- `init_netbuf`
- `free_netbuf`
- local `inet_ntoa`, `inet_aton`, `isdigit`, `atoi`

## Root Mount Flow

`mount_root()` is called with a logical name such as `root`, a path buffer, an NFS protocol version, NFS mount arguments, and VFS flags.

The flow is:

1. Initialize boot network configuration once with `init_config()`.
2. Allocate a server address netbuf.
3. Repeatedly call `getfile()` until it does not return `ETIMEDOUT`.
4. Depending on requested NFS version:
   - NFSv2: call `mountnfs()` through mount protocol v1.
   - NFSv3: call `mountnfs3()` through mount protocol v3.
   - NFSv4: ping NFS program version 4 over TCP and use the standard NFS port.
5. Reject NFSv4 root when `nfs4_no_diskless_root_support` is set.
6. Choose TCP or UDP `knetconfig`.
7. Parse root mount options with `init_mountopts()`.
8. Copy the selected netconfig into caller-provided `args->knconf`.

The file prefers TCP when a server responds to NFS NULLPROC over TCP, otherwise it uses UDP.

## Boot Configuration Sources

`init_config()` extracts the boot network device path, interface name, and physical point of attachment from `rootfs`. It sets clone-device `rdev` values for UDP and TCP, then tries three configuration sources in order:

1. `bp_netconfig()` from boot properties
2. `dhcpinit()` from an OBP-provided DHCP ACK packet
3. `whoami()` through RARP and bootparamd

If all fail, it warns that the interface did not respond.

`bp_netconfig()` uses boot properties such as host IP, subnet mask, router IP, server path, server name, root options, and server IP. If enough data is present, it configures the interface and adds a default route.

`dhcpinit()` parses the cached DHCP ACK packet, sets hostname and NIS domain when provided, configures netmask and broadcast, brings up the interface with `IFF_DHCPRUNNING`, and adds router routes.

`cacheinit()` extracts NFS root server path/name/IP and root options from boot properties and DHCP vendor options. It understands root path forms such as `nfs://server/path`, `server:/path`, and `/path`.

`whoami()` uses RARP to discover the client IP address, broadcasts a bootparams WHOAMI request, sets hostname/domain name, records the bootparam server address, and adds a router if bootparamd provides one.

## RARP And Interface Setup

`revarp_myaddr()` opens the boot network device through LDI, attaches and binds DLPI to `ETHERTYPE_REVARP`, obtains the Ethernet address, sends RARP requests, and sets the resulting IP address on the network interface.

`revarp_start()` formats a DLPI unitdata request containing an Ethernet RARP packet and sends it. It loops until `revarpinput()` fills the client IP address.

`revarpinput()` waits with a timeout for DLPI messages, validates message structure, accepts only IP RARP replies for the local Ethernet address, and copies the target protocol address into the caller’s netbuf.

`dlifconfig()` sets address, broadcast address, netmask, and interface flags using kernel stream ioctls.

## NFS Mount Protocol

`mountnfs()` discovers the mount daemon port for mount protocol v1 through `pmap_kgetport()`, sends `MOUNTPROC_MNT`, receives a v2 filehandle, then sets the server port to `NFS_PORT`. It defaults to UDP but switches to TCP if `ping_prog()` succeeds for NFSv2 over TCP.

`mountnfs3()` does the same for mount protocol v3. It handles `RPC_PROGVERSMISMATCH` as `EPROTONOSUPPORT`, decodes the variable-length v3 filehandle, frees XDR-allocated mount result state, and switches to TCP if NFSv3 NULLPROC succeeds over TCP.

NFSv4 does not use the mount protocol here; it simply verifies that NFS program version 4 responds over TCP and uses `NFS_PORT`.

## Portmapper And RPC Helpers

`pmap_kgetport()` first queries the old portmapper `PMAPPROC_GETPORT`. If portmapper is unavailable, it falls back to rpcbind `RPCBPROC_GETADDR` and converts the universal address to a port.

`pmap_rmt_call()` supports broadcast-style remote calls. It first tries portmapper `PMAPPROC_CALLIT`, then rpcbind remote call if portmapper is unavailable. It updates response address and port on success.

`mycallrpc()` creates a kernel TLI RPC client, performs one RPC call with a given timeout/retry count, destroys the auth handle and client, and returns the RPC status.

The local XDR routines are minimal copies needed for early boot because the full generated mount XDR code is not directly used here.

## Root Mount Options

`init_mountopts()` starts with defaults:

- `NFSMNT_NOCTO`
- `NFSMNT_LLOCK`
- `NFSMNT_INT`
- attribute-cache min/max defaults

It optionally obtains `rootopts` through `getfile("rootopts")`, then parses an option list mirroring the userland NFS mount command.

Handled options include readonly/readwrite, soft/hard/semisoft, grpid, intr/nointr, noac, nocto, rsize, wsize, timeo, retrans, actimeo, acreg/acdir min/max, llock, version, proto, noprint, and forcedirectio.

Some options are ignored because they are defaults or not meaningful during root boot. Unsafe root options such as nosuid, nodevices, nosetuid, noexec, and remount produce warnings. Security options are ignored because root is mounted with AUTH_UNIX in this path.

Read size is bounded: if unspecified, NFSv4 defaults to 32 KiB and older NFS defaults to 8 KiB. Values below 512 are raised, and UDP values above 56 KiB are trimmed.

## Notable Invariants

- Diskless boot uses IPv4-only assumptions throughout this file.
- The root network interface must be configured before server discovery and mount protocol calls.
- NFSv4 diskless root is deliberately disabled by `nfs4_no_diskless_root_support`.
- TCP is preferred when available, but UDP remains the fallback.
- Boot property and DHCP cached data can bypass bootparam RPC discovery.
- Root mount option parsing is single-threaded and stores root options in static buffers.
- Portmapper fallback to rpcbind is built into both port lookup and remote-call paths.

## Dependencies

This file depends on:

- Kernel TLI and RPC client APIs
- DLPI/LDI for direct network-device RARP during boot
- Boot properties and DHCP option parsing
- NFS mount argument structures and NFS protocol constants
- Portmapper/rpcbind protocol definitions
- Kernel stream ioctls for interface and route configuration
- `nfs_common.c` dynamic root flow, which calls `mount_root()`

## Research Notes

This file is early-boot infrastructure rather than ordinary runtime NFS client code. The audit hotspots are static global boot state, string and option parsing, IPv4-only assumptions, XDR allocation/freeing for mount v3 results, netbuf lifetime, route/interface ioctl error handling, and the protocol fallback rules that determine whether diskless boot proceeds or falls back to another NFS version.

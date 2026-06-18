# File Research: sources/os/bsd/openbsd-src/sbin/ifconfig/ifconfig.c

## Purpose
`ifconfig.c` is OpenBSD `ifconfig`'s main implementation. It parses command-line options, dispatches interface commands through a large command table, reads and writes interface state through network ioctls, prints interface status, and hosts support for address families, media selection, 802.11, bridges, trunks, CARP, pfsync, tunnels, MPLS/PWE3, PPPoE/SPPP, pflow, WireGuard, UMB mobile broadband, link-layer addresses, groups, rdomains, descriptions, and hardware capabilities.

## Global State and Dispatch Model
The file keeps process-wide command state in globals: `ifr`, `ifr6`, `in_addreq`, `in6_addreq`, `ifname`, `flags`, `xflags`, `metric`, `mtu`, `llprio`, `sock`, selected address family `af`, `afp`, and deferred-action flags. The `cmds[]` table maps user tokens to:
- a parameter model: immediate integer, `NEXTARG`, `NEXTARG0`, or `NEXTARG2`;
- a deferred action flag such as media, join, or WireGuard;
- either one-argument or two-argument handler functions.

Bridge functions come from `brconfig.c`; transceiver SFF parsing comes from `sff.c`; shared prototypes are in `ifconfig.h`.

## Main Control Flow
`main()` handles these primary modes:
- no arguments: unveil no filesystem visibility, set `aflag`, and print all interfaces;
- option parsing: `-a`, `-A`, `-g`, `-C`, and `-M lladdr`;
- optional address-family selection (`inet`, `inet6`);
- cloner listing (`-C`);
- group attribute read/write (`-g`);
- special early `create`, because normal `getinfo()` would fail before the interface exists;
- interface probing via `getinfo()`;
- command-table dispatch, including bridge `rule` special handling;
- deferred processing for WireGuard, 802.11 join, and media commands;
- final address deletion/addition via address-family-specific ioctls.

The program uses `unveil()` to restrict filesystem access. Unless `rulefile` is present, it unveils only resolver, hosts, and services files for address/name resolution.

## Address Families
`afs[]` defines `inet` and `inet6` behavior:
- `in_status()`, `in_getaddr()`, and `in_getprefix()` handle IPv4 display and parsing.
- `in6_status()`, `in6_alias()`, `in6_getaddr()`, and `in6_getprefix()` handle IPv6 display, scoped link-local fixups, prefix lengths, lifetimes, and flags.
- `setifaddr()`, `setifdstaddr()`, `setifnetmask()`, `setifprefixlen()`, and `notealias()` stage address changes in global request structs; actual ioctl submission is delayed until flags and prefixes are settled.
- IPv6 defaults unspecified prefix length to `/64`, or `/128` for point-to-point destination addresses.

## Interface Discovery and Printing
- `getsock()` caches a datagram socket by address family.
- `getinfo()` reads flags, extended flags, metric, MTU, rdomain, and link-layer priority; it can create the interface if requested.
- `printif()` walks `getifaddrs()`, supports group-name expansion, exact interface matching for names ending in digits, prefix matching for group-like names, and prints link-layer status before protocol addresses.
- `status()` is the main per-interface status printer. It prints flags, rdomain, metric, MTU, link-layer address, description, index, priority, llprio, keepalive, patch peer, encapsulation, protocol-specific status blocks, media, link status, optional transceiver data, wireless state, address-family status, tunnel state, and bridge status.

## Command Families
Core setters use ioctls directly:
- flags and xflags: `setifflags()`, `setifxflags()`, `addaf()`, `removeaf()`;
- MTU, metric, llprio, priority, rdomain, description, patch pair, random/static lladdr;
- group membership and group CARP demotion;
- interface cloning via `SIOCIFCREATE`, `SIOCIFDESTROY`, and `SIOCIFGCLONERS`;
- `findmac()` finds a physical non-cloned interface by MAC address.

## Media Handling
Media commands are deferred so multiple options can be combined safely:
- `init_current_media()` fetches current media with `SIOCGIFMEDIA`.
- `setmedia()`, `setmediamode()`, `unsetmediamode()`, `setmediaopt()`, `unsetmediaopt()`, and `setmediainst()` validate command ordering and update `media_current`, `mediaopt_set`, and `mediaopt_clear`.
- `process_media_commands()` commits with `SIOCSIFMEDIA`.
- `print_media_word()` renders media in status or command syntax.
- Lookup helpers use `IFM_*_DESCRIPTIONS` tables.

## 802.11 Wireless Support
The file manages SSID/join state, WEP/WPA settings, scanning, and status:
- `get_string()`, `len_string()`, and `print_string()` parse/format ASCII or hex network IDs and keys.
- `setifnwid()` and `setifjoin()` are mutually exclusive; `process_join_commands()` submits deferred `SIOCS80211JOIN`.
- WEP/WPA handlers configure nwkey, WPA protocol sets, AKMs, ciphers, group cipher, and WPA PSK. WPA passphrases are converted with `pkcs5_pbkdf2()`.
- `ieee80211_status()` reads many wireless ioctls and prints nwid/join, channel, BSSID, RSSI, nwkey, WPA settings, power-save, flags, and association failures.
- `join_status()`, `ieee80211_listchans()`, and `ieee80211_listnodes()` display join lists, available channels, and scan results.

## Encapsulation, VLAN, Tunnels, MPLS, and PWE3
Encapsulation state is grouped in `struct ifencap`:
- `getencap()` prints `vnetid`, `parent`, optional flow ID, TX priority, and RX priority.
- `setvnetid()`, `delvnetid()`, `setifparent()`, `delifparent()`, `setvnetflowid()`, and priority setters use the corresponding `SIOC*` ioctls.
- `phys_status()` and tunnel setters manage local/remote physical tunnel addresses, TTL, DF, ECN, and tunnel rdomain.
- MPLS and PWE3 support prints labels, PWE3 neighbor labels, control word, FAT state, and sets/unsets labels/neighbors/options.

## Aggregation and Redundancy Protocols
- Trunk support sets ports, protocol, LACP mode/timeout, and prints aggregate/port LACP state.
- CARP support prints one or many VHIDs and sets password, VHID, advbase, advskew, peer, state, device, node list, and balancing mode.
- pfsync support sets syncdev, syncpeer, max updates, defer flag, and prints active sync settings.
- pflow support parses IPv4/IPv6 sender/receiver endpoints, sets protocol version, and prints sender/receiver/version status.
- PPPoE support prints discovery/session state and sets device, service, and access concentrator.
- SPPP support reads/writes auth/peer auth protocol, names, secrets, peer flags, DNS info, and phase state.

## WireGuard Support
WireGuard configuration is built in a growable `wg_data_io` buffer:
- `WG_LOAD_KEY` validates base64 key length and decodes keys.
- `ensurewginterface()` and `growwgdata()` allocate and resize the packed interface/peer/AIP request layout while preserving offsets.
- Peer commands add/remove peers, descriptions, endpoints, allowed IPs, PSKs, persistent keepalive, listen port, private key, and routing table.
- `process_wg_commands()` submits `SIOCSWG`.
- `wg_status()` reads variable-sized `SIOCGWG` output, prints interface port/rtable/public key, and with aliases enabled prints peers, descriptions, PSK presence, endpoints, counters, last handshake age, and allowed IPs.

## UMB Mobile Broadband Support
Non-`SMALL` UMB support uses MBIM value-description tables:
- `umb_status()` prints network errors, roaming/registration, supported classes, internal state, cell class, RSSI, speed, SIM/PIN state, subscriber identifiers, device/firmware info, phone/APN/provider info, and DNS servers.
- `umb_setpin()`, `umb_chgpin()`, `umb_puk()`, `umb_apn()`, `umb_setclass()`, and `umb_roaming()` read/update `umb_parameter`.
- `utf16_to_char()` and `char_to_utf16()` convert ASCII-compatible strings to/from UTF-16LE fields used by UMB ioctls.

## Formatting Helpers
- `printb()` and `printb_status()` render kernel `%b` bit descriptions.
- `prefix()` computes a contiguous prefix length and rejects non-contiguous masks by returning zero in invalid cases.
- `sec2str()` currently returns decimal seconds.
- `usage()` prints the concise command syntax.

## Error Handling and Risks
The implementation is intentionally ioctl-centric and exits on command failure with `err()`/`errx()` while status paths often tolerate unsupported ioctls. Risk areas include heavy reliance on global mutable structs, command ordering subtleties in deferred media/join/WireGuard paths, variable-size ioctl buffer resizing, packed WireGuard offset arithmetic, ambiguous parsing of `host:port` versus IPv6 literals in some tunnel/pflow paths, and broad ABI coupling to OpenBSD kernel networking headers.

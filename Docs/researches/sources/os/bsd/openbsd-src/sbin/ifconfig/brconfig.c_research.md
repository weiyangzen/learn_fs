# File Research: sources/os/bsd/openbsd-src/sbin/ifconfig/brconfig.c

## Purpose
`brconfig.c` is the non-`SMALL` bridge-control companion for OpenBSD `ifconfig`. It implements bridge, TPMR-like bridge status, bridge-member flag changes, VLAN/PVLAN configuration, forwarding-table inspection, VXLAN-style endpoint address handling, and bridge packet-filter rule parsing. The public entry points are declared in `ifconfig.h` and are invoked from `ifconfig.c` command-table rows such as `add`, `del`, `tagged`, `pvlan`, `static`, `endpoint`, `rules`, and `rulefile`.

## Compilation and Integration
The entire file is guarded by `#ifndef SMALL`, so install-media or reduced builds omit these features. It depends on global state from `ifconfig.c`: `sock`, `ifname`, `aflag`, `ifaliases`, and `printb()`. It uses OpenBSD bridge kernel ABI structures and ioctls from `<net/if_bridge.h>`, Ethernet parsing from `<netinet/if_ether.h>`, `getnameinfo()` for endpoint display, and `clock_gettime(CLOCK_MONOTONIC)` for virtual address age output.

## Major Data and Formatting Helpers
- `VID_SEP` is `'@'`, used to encode a VLAN-scoped bridge address as `mac@vid`.
- `IFBAFBITS` and `IFBIFBITS` are `%b`-style bit-name strings passed to `printb()`.
- `PV2ID()` splits a bridge priority/vector ID into priority plus Ethernet address bytes.
- `stpstates`, `stpproto`, and `stproles` convert kernel STP/RSTP numeric fields into user-facing text.

## Bridge Member Flag Operations
Small setters like `setdiscover()`, `unsetdiscover()`, `setlearn()`, `unsetlearn()`, `setlocked()`, `unsetlocked()`, `setstp()`, `setedge()`, `setptp()`, and related auto variants delegate to:
- `bridge_ifsetflag()`: fetches member flags with `SIOCBRDGGIFFLGS`, ORs the requested writable flag after masking `IFBIF_RO_MASK`, and commits with `SIOCBRDGSIFFLGS`.
- `bridge_ifclrflag()`: fetches member flags, clears the requested bits and read-only mask bits, then commits.
- `addlocal()`: adds a local bridge port via `SIOCBRDGADDL`, but first enforces that the member name starts with `vether`.

## Bridge Membership and STP Status
- `bridge_add()`, `bridge_delete()`, `bridge_addspan()`, and `bridge_delspan()` wrap `SIOCBRDGADD`, `SIOCBRDGDEL`, `SIOCBRDGADDS`, and `SIOCBRDGDELS`.
- `bridge_cfg()` reads bridge parameters with `SIOCBRDGGPARAM`, prints priority, timers, hold count, and protocol, then prints designated/root bridge details unless `aflag` suppresses extra detail.
- `bridge_list()` grows an `SIOCBRDGIFS` buffer until large enough, prints each bridge member/span with flags, port number, priority, path cost, PVID/untagged state, protected domains, STP state/role, tagged VLAN map, and bridge rules for the member.
- `is_bridge()` probes `SIOCBRDGRTS`; `ENETDOWN` still counts as bridge-like.
- `is_tpmr()` identifies TPMR devices by `tpmr` prefix.
- `bridge_status()` is the status orchestrator called by `ifconfig.c`. It handles TPMR with only member listing, otherwise prints bridge parameters, PVLANs, members, and address cache unless global display flags suppress aliases.

## Timers, Priorities, and Bridge Parameters
The file validates numeric arguments with `strtonum()` before ioctl submission:
- `bridge_timeout()` -> `SIOCBRDGSTO`
- `bridge_maxage()` -> `SIOCBRDGSMA`
- `bridge_priority()` / `spanpriority` -> `SIOCBRDGSPRI`
- `bridge_fwddelay()` -> `SIOCBRDGSFD`
- `bridge_hellotime()` -> `SIOCBRDGSHT`
- `bridge_maxaddr()` -> `SIOCBRDGSCACHE`
- `bridge_holdcnt()` -> `SIOCBRDGSTXHC`
- `bridge_proto()` validates against `stpproto[]` and writes `SIOCBRDGSPROTO`.
- `bridge_ifprio()`, `bridge_ifcost()`, and `bridge_noifcost()` set per-member priority/path cost.

## VLAN and Private VLAN Handling
- `bridge_pvid()` maps `default`, `none`, `passthrough`/`passthru`, or a numeric VID into `ifbr_pvid` and applies `SIOCBRDGSPVID`.
- `bridge_unpvid()` sets `IFBR_PVID_NONE`.
- `bridge_set_vidmap()` parses `all`, `none`, or comma/range lists, with optional `+`, `-`, or `=` operation prefixes. It fills `ifbrvidmap.ifbrvm_map` and uses `SIOCBRDGSVMAP`.
- `bridge_unset_vidmap()` resets the tagged map to all zero bits.
- `bridge_vidmap()` reads `SIOCBRDGGVMAP` and compresses set VID bits into ranges for display.
- `bridge_pvlan_primary_op()` and `bridge_pvlan_secondary_op()` implement PVLAN primary, isolated, and community add/delete through `SIOCBRDGADDPV` and `SIOCBRDGDELPV`.
- `bridge_pvlans()` iterates PVLAN primary and community mappings with `SIOCBRDGNFINDPV`.

## Forwarding Address Cache and Endpoints
- `bridge_addaddr()` accepts either a plain Ethernet address or `mac@vid`. Plain entries use `ifbareq` and `SIOCBRDGSADDR`; VLAN-scoped entries use `ifbvareq` and `SIOCBRDGSVADDR`.
- `bridge_deladdr()` deletes plain or VLAN-scoped entries via `SIOCBRDGDADDR` or `SIOCBRDGDVADDR`.
- `bridge_addendpoint()` resolves an endpoint host with `getaddrinfo()`, stores the resolved sockaddr in `ifba_dstsa`, and adds a static bridge address.
- `bridge_delendpoint()` removes a static endpoint by Ethernet address.
- `bridge_vaddrs_try()` reads newer virtual address records with `SIOCBRDGVRTS`, prints optional VID, member name, age since last use, flags, and tunnel endpoint.
- `bridge_addrs()` is the older address-table path using `SIOCBRDGRTS`.

## Rule Handling
- `bridge_rules()` grows an `SIOCBRDGGRL` buffer, then prints each `ifbrlreq` via `bridge_showrule()`.
- `bridge_rule()` parses one bridge rule of the shape `block|pass [in|out|in/out] on ifs [src mac] [dst mac] [tag name] [arp|rarp ...]`, fills an `ifbrlreq`, and installs it with `SIOCBRDGARL`.
- `bridge_arprule()` parses ARP/RARP predicates such as request/reply, SHA/THA Ethernet addresses, and SPA/TPA IPv4 addresses.
- `bridge_rulefile()` reads whitespace-tokenized rules from a file, ignores comments and blank lines, limits each rule to `MAXRULEWORDS`, and passes each rule to `bridge_rule()`.
- `bridge_badrule()` prints a normalized parse error including file line number when available.
- `bridge_flushrule()` clears rules for a member with `SIOCBRDGFRL`.

## Error Handling and Risks
The file consistently fails fast with `err()`/`errx()` for invalid user input and ioctl failures that indicate command failure. Display paths tolerate some unsupported ioctls (`ENOTTY`, `ENOENT`, `ENETDOWN`) to keep status output useful across bridge feature versions. Notable risks are ABI coupling to `if_bridge.h`, manual variable-length ioctl buffer growth, and rule parser ambiguity if new bridge-rule grammar is added without preserving current token ordering.

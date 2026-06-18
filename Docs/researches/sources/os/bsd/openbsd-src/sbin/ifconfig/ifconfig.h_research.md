# File Research: sources/os/bsd/openbsd-src/sbin/ifconfig/ifconfig.h

## Purpose
`ifconfig.h` is the shared local header for OpenBSD `sbin/ifconfig`. It exposes globals owned by `ifconfig.c` plus function prototypes implemented by `ifconfig.c`, `brconfig.c`, and `sff.c`.

## Exported Globals
- `aflag`: global "all interfaces" status mode.
- `ifaliases`: controls whether alias/extra details are printed.
- `sock`: current ioctl socket shared by helper files.
- `ifname[IFNAMSIZ]`: selected interface name used by nearly every ioctl helper.

## Shared Formatting
- `printb(char *, unsigned int, unsigned char *)` is exported so bridge code can print bridge flag bitfields using the same `%b`-style formatter as `ifconfig.c`.

## Bridge API Surface
Most declarations are bridge control/status functions implemented in `brconfig.c`. They cover:
- member flags: discover, block non-IP, learn, locked, private VLAN port tags, STP, edge, autoedge, point-to-point, autoptp;
- membership: add/delete member, add/delete span, add local;
- forwarding database: flush, flushall, static address add/delete, endpoint add/delete, address display, virtual address display, max address count;
- timers and STP settings: hello time, forward delay, max age, protocol, priority, hold count, timeout;
- per-port settings: protected domains, PVID/untagged behavior, tagged VID map, interface priority, interface cost;
- PVLAN settings: primary, isolated, and community add/delete;
- rules: display, rulefile, flushrule, and direct `bridge_rule()` parsing;
- bridge detection and status.

## SFF API Surface
- `if_sff_info(int)` is implemented by `sff.c` and used by `ifconfig.c` for `transceiver`, `sff`, and `sffdump` output.

## Integration Notes
This header intentionally contains declarations only. It relies on included translation units already having the required system types visible, especially `IFNAMSIZ`. The separation keeps `ifconfig.c` as the command dispatcher while allowing bridge and transceiver logic to live in separate files without duplicating global declarations.

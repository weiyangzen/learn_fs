# File Research: sources/os/bsd/freebsd-src/sbin/etherswitchcfg/etherswitchcfg.c

Implements `etherswitchcfg`, a command-line control utility for `/dev/etherswitchN`.

Key responsibilities:
- Opens a control device, default `/dev/etherswitch0`.
- Reads switch info and configuration via `IOETHERSWITCHGETINFO` and `IOETHERSWITCHGETCONF`.
- Prints switch configuration, port state, VLAN groups, media status, and supported media.
- Sets per-port PVID, media subtype, media options, LED style, and port flags.
- Sets VLAN group VID and membership/untagged masks.
- Sets global VLAN mode.
- Reads/writes raw switch registers and PHY registers.
- Dumps or flushes the address translation table.

Command model:
- Maintains a current mode: none, config, port, VLAN group, register, PHY register, or ATU.
- Mode transitions print the just-modified object before returning to command mode.
- `cmds[]` maps subcommands to modes, expected argument counts, and handler functions.

Important data:
- `struct cfg`: fd, verbosity, media listing flag, control path, switch configuration, switch info, current mode, and selected unit.
- `ledstyles[]`: maps user LED style strings to enum order.
- VLAN IDs validated against `IEEE802DOT1Q_VID_MAX`.

Notable behavior:
- Port flags support positive and negative forms such as `addtag` and `-addtag`.
- VLAN members use strings like `1,2t,3`, with suffix `t` meaning tagged.
- Media parsing/printing delegates to helpers in `ifmedia.c`.
- ATU dump iterates table entries with `IOETHERSWITCHGETTABLEENTRY`.

Risks and constraints:
- Mostly thin ioctl plumbing; correctness depends on kernel driver support.
- Some handlers do minimal parse validation, e.g. `strtol()` without full end-pointer checks in several command paths.
- Usage string starts with `etherswitchctl`, likely a stale name, while the program is `etherswitchcfg`.

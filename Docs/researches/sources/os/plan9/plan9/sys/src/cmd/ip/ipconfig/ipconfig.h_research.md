# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ipconfig/ipconfig.h

Defines shared state, constants, packet layouts, globals, and prototypes for Plan 9 `ipconfig`.

Key contents:
- `Conf` stores requested/local interface configuration, learned DHCP/NDB values, hardware/client IDs, DHCP lease state, and IPv6 router-advertisement/prefix parameters.
- `Ctl` stores extra device control strings from `-c`.
- Declares global config and flags such as `conf`, `noconfig`, `ipv6auto`, `dodhcp`, `debug`, `plan9`, `dupl_disc`, `myifc`.
- Declares DHCP option helpers, interface configuration functions, NDB functions, IPv6 entry points, and logging helpers.
- Defines IPv6/ICMPv6 packet structures for router solicitation/advertisement, link-layer address option, prefix option, and MTU option.
- Defines protocol numbers, RA flags, IPv6 defaults, and helper prototypes `ea2lla` and `ipv62smcast`.

Integration points:
- Included by `main.c`, `ipv6.c`, and `ppp.c` under `ipconfig`.
- Bridges Plan 9 IP stack control-file operations, DHCP, NDB, and IPv6 RA logic.

Risks and notes:
- `Conf` is a global mutable state bag shared across forked helper processes.
- IPv6 support is explicitly partial: comment notes no IPv6 lease support.

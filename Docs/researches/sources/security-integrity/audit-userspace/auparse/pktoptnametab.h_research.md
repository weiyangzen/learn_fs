<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/pktoptnametab.h -->
# sources/security-integrity/audit-userspace/auparse/pktoptnametab.h

## Purpose
Maps packet socket option names for `SOL_PACKET` socket option interpretation.

## Important APIs, types, and functions
The `_S` table includes packet membership, rings, statistics, auxdata, versioning, reserve, loss, fanout, qdisc bypass, rollover stats, ignore outgoing, and VNET header size options.

## Control flow
Generated `pktoptname_i2s` is called by `interpret.c:print_pkt_opt_name` when syscall context indicates `SOL_PACKET`.

## State and persistence behavior
Static table only.

## Dependencies and integration points
Tracks `include/uapi/linux/if_packet.h`; selected from `print_a2` based on socket option level.

## Risks and test signals
Risks are missing newer packet options and wrong level detection. Tests should exercise known packet options and unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/pktoptnametab.h -->

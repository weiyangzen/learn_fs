# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/ppp.h

Shared PPP declarations: buffer blocks, protocol constants, state structures, compression interfaces, PPP session state, packet layouts, and external function prototypes.

Key contents:
- `Block` packet buffer definition and block helper prototypes.
- PPP framing constants, protocol IDs, PPP phases, LCP codes/options, auth protocols, CHAP/PAP states, link states, CCP/ECP/IPCP options, option flag masks, timeout/MTU/default constants.
- `Pstate` stores per-control-protocol negotiation state.
- `Chap` stores authentication state and challenge.
- `Qualstats` and `Qualpkt` model link quality monitoring.
- `Comptype` and `Uncomptype` are compression virtual tables for MPPC/thwack.
- `PPP` is the main session object, containing fds, addresses, negotiated flags, compression/encryption/auth state, LQM counters, and statistics.
- Declares public PPP APIs `pppread`, `pppwrite`, `pppopen`, compression/checksum helpers, MPPC/thwack type tables, and `netlog`.

Integration points:
- Included by all files under `cmd/ip/ppp`.
- Defines the ABI between PPP core, block allocator, VJ compression, MPPC compression, checksum helpers, and optional thwack modules.

Risks and notes:
- `PPP` is a large mutable shared object passed across forked processes with `RFMEM`.
- IPCP DNS/WINS flags are manually mapped above bit 8 because option numbers exceed direct low-bit range.

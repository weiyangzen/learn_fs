# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/pppoe_disc.c

`snoopy` PPPoE discovery/session decoder.

Key behavior:
- Parses PPPoE version/type, code, session id, and payload length.
- Defines shared filtering fields for version, type, code, and session id.
- `pppoe_disc` prints discovery header and terminates walk.
- `pppoe_sess` prints session header and demuxes payload to PPP.

Integration:
- Reached from Ethernet EtherTypes `0x8863` and `0x8864`.
- `pppoe_sess.c` is only a placeholder; actual `Proto pppoe_sess` is here.

Risks and notes:
- Discovery tags are not decoded here, only the fixed PPPoE header.

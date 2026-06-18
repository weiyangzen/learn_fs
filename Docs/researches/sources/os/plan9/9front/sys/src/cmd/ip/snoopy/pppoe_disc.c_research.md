# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/pppoe_disc.c

This snoopy module implements both PPPoE discovery and PPPoE session protocol objects. It parses the PPPoE fixed header and optionally demuxes session payloads to PPP.

Key behavior:
- Header fields: version/type byte, code, session ID, payload length.
- Filters support version (`v`), type (`t`), code (`c`), and session ID (`s`).
- `pppoe_disc` prints header fields and stops.
- `pppoe_sess` prints header fields then demuxes to `ppp`.
- A `BUG` comment notes discovery tag types are not fully printed.

Research notes:
- `p_compiledisc()` and `p_compilesess()` have commented-out mux compilation, so filters are field-only.

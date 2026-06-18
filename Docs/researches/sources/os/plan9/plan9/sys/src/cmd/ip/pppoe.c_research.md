# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/pppoe.c

User-level PPP over Ethernet client for RFC 2516 discovery and session framing.

Key behavior:
- Parses PPPoE client options for access concentrator, service name, PPP net mount, MTU, keyspec, primary route, and debug.
- Builds PADI and PADR discovery packets with service-name, AC-name, and optional AC-cookie tags.
- Reads discovery replies with alarm-based exponential timeout.
- Selects matching PADO/PADS packets by service name and optional access concentrator name.
- After session establishment, creates a pipe:
  - One child reads PPP bytes, wraps them in PPPoE session Ethernet frames, and writes to the Ethernet session fd.
  - Another child reads PPPoE session frames, validates session id/code/type, and writes payload bytes to PPP.
- `execppp()` execs `/bin/ip/ppp` with `-F`, MTU, and optional auth/network flags.

Integration:
- Uses Plan 9 `dial()` on Ethernet packet types `0x8863` and `0x8864`.
- Hands a byte stream to `/bin/ip/ppp`.

Risks and notes:
- Packet validation checks type/length but not all PPPoE tag semantic errors.
- Discovery state is global.
- Debug helpers dump packet headers, tags, and optional hexdumps.

# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/ninep.c

This snoopy protocol module decodes 9P messages. It uses `convM2S()` from Plan 9 fcall support and `%F` formatting to render a packet as an `Fcall`.

Key behavior:
- Attempts to decode the full remaining payload as one 9P message.
- Rewrites embedded newlines in the formatted `Fcall` as backslashes so snoopy packet output remains one logical line.
- Falls back to `dump.seprint()` if conversion fails.
- Sets `m->pr = nil`, making 9P a terminal decoder.

Research notes:
- Registered as `Proto ninep`; muxed from TCP ports including 564 and several CPU/exportfs ports, and from UDP port 6346.

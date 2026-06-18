# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/bootp.c

`snoopy` BOOTP decoder and DHCP/Plan 9 BOOTP demux.

Key behavior:
- Parses BOOTP fixed header including op, hardware fields, xid, flags, client/server/gateway addresses, hardware address, server name, boot file, and option magic.
- Filters on client address, server address, or option magic.
- Demuxes generic DHCP magic to `dhcp`, Plan 9 magic to `plan9bootp`, otherwise dump.
- Formats fixed BOOTP metadata and optional server/file strings.

Integration:
- Reached from UDP port 67 demux.

Risks and notes:
- Uses a minimum check up to `sname`, not full fixed BOOTP header, before accessing later fields.

# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/bootp.c

This module decodes BOOTP headers and demuxes option payloads. It understands standard BOOTP fields, Plan 9 BOOTP magic, and generic DHCP magic.

Filters support client address and server address, plus protocol selection by option magic. The mux table routes generic DHCP magic to `dhcp`, Plan 9 magic to `plan9bootp`, and otherwise to `dump`.

`p_seprint` prints request/reply type, hardware type/length/hops, transaction id, seconds, flags, client/your/server/gateway IPs, client hardware address, magic, optional server name, and boot file. It then positions `m->ps` at the option data and demuxes based on `optmagic`.

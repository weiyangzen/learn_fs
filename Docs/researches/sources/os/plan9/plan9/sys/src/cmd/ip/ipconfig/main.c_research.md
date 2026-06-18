# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ipconfig/main.c

Main implementation of Plan 9 `ipconfig`: command-line parsing, interface bind/add/remove/unbind, DHCP client, DHCP option encoding/decoding, NDB integration, lease renewal, and primary-interface publication.

Key behavior:
- CLI supports media selection (`ether`, `gbe`, `ppp`, `loopback`, etc.), verbs (`add`, `remove`, `unbind`, `add6`, `ra6`), DHCP/NDB modes, IPv6 autoconfig, primary selection, custom DHCP option requests, gateway/host/MTU, alternate net mount point, and PPP baud.
- `doadd` binds/configures the interface, performs IPv6 setup if requested, otherwise uses explicit address, NDB lookup, or DHCP; publishes learned config to `/net/ndb` when primary.
- `doremove` and `dounbind` locate matching interfaces and write `remove`/`unbind` to the relevant `ipifc/*/ctl`.
- `binddevice`, `controldevice`, `lookforip`, and `ip4cfg` handle Plan 9 control-file operations for IP stack binding and logical IPv4 address addition.
- DHCP flow:
  - `dhcpquery` opens UDP port 68, sends discover/request, and loops on receive/timer.
  - `dhcpsend` builds BOOTP/DHCP packets with client ID, hostname, vendor class, parameter request list, lease/server/address options.
  - `dhcprecv` validates replies, handles Offer/Ack/Nak, extracts address, mask, gateway, DNS, NTP, hostname/domain, custom requested options, and Plan 9 vendor options.
  - `dhcpwatch` forks a renewal daemon, renews at half lease, reconfigures on expiration, and republishes NDB.
- DHCP option helpers `optadd*`, `optget*`, `parseoptions`, and `parsebootp` encode/decode and sanity-check options.
- NDB flow:
  - `ndbconfig` looks up config by Ethernet address.
  - `putndb`, `writendb`, `putaddrs`, `getndb`, `tweakservers` publish and refresh `/net/ndb`, `cs`, and `dns`.
- `addoption`, `optgetx`, and `getoptions` support user-requested extra DHCP options and append them to NDB text.

Integration points:
- Includes `dhcp.h`, `ipconfig.h`, `ndb.h`, Plan 9 `/net` control files, and `pppbinddev` from `ipconfig/ppp.c`.
- Shares IPv6 entry points with `ipv6.c`.

Risks and notes:
- Most state lives in global `conf`; forked renewal/RA helpers inherit mutable state.
- `parseoptions` writes an `OBend` sentinel at the end of the provided buffer when no end option appears, mutating receive storage.
- `getoptions` does not guard `s == nil` before using it in `smprint`, which may matter for requested options absent in a reply.

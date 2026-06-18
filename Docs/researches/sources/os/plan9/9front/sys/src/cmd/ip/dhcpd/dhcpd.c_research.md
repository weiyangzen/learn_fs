# File Research: sources/os/plan9/9front/sys/src/cmd/ip/dhcpd/dhcpd.c

Main IPv4 BOOTP/DHCP server. It parses configured dynamic pools, listens on `bootp`, reads the latest queued packet, validates interface/relay context, parses DHCP options, finds static ndb host info, and dispatches BOOTP or DHCP handling.

Implements RFC2131-style handling for Discover, Request, Decline, Release, and Inform. Static bindings are answered from ndb; dynamic bindings come from `db.c`, with lease offers, commit checks, NAKs, conflict handling, and release support.

Also serves legacy BOOTP, including Plan 9 vendor fields, generic RFC1048 options, boot file selection, TFTP server selection, and ARP entry injection for unicast replies. `miscoptions` supplies subnet mask, router, host/domain, DNS, WINS, SMTP/POP/WWW/root/NTP/time servers, TFTP/bootfile, DNS search domains, and Plan 9 vendor options.

Command-line flags control debug, mute modes, BOOTP disabling, PPTP-only behavior, slow replies, IPv6-text Plan 9 options, net mountpoint, ndb file, homedir, and lease bounds.

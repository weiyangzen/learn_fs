# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ipconfig/ipconfig.h

Shared declarations for `ipconfig`. It defines verb/media constants, the central `Conf` structure containing local interface state, learned IPv4/IPv6/DHCP/RA parameters, server addresses, client IDs, DUID, and prefix lifetimes, plus queued device control messages.

It declares globals and cross-file functions for DHCPv4, DHCPv6, IPv6 RA/prefix handling, route updates, ndb updates, utility parsing/formatting, warning/debug output, and PPP binding.

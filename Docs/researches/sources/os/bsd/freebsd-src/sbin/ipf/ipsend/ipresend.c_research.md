# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/ipresend.c

This is the `ipresend` command-line frontend. It resends captured packets from an input format reader through the `ipsend` packet-send backend.

It parses device, gateway, MTU, input file, raw mode, and reader-format switches. Reader formats include `iphex`, `pcap`, and `iptext` when IPFilter readers are available. It resolves an optional gateway, chooses a default device, prints send parameters, and calls `ip_resend()`.

Important dependencies include `ipsend.h`, external `struct ipread` readers, and global `opts`.

Implementation notes and risks:
- The `-m` option case lacks a `break`, so after setting MTU it falls through to `-r` and sets `resend = optarg`; this may be intentional shorthand or a bug.
- The usage text mentions `-R filename`, but the parser treats `-R` as raw mode without an argument.
- The tool is IPv4/Ethernet oriented.

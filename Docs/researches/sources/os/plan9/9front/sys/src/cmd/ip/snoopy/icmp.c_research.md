# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/icmp.c

This module decodes ICMPv4 packets. It supports filtering by type and selecting embedded IPv4 payloads for error messages.

`p_filter` consumes the ICMP header, compares type, or accepts embedded-IP selection for unreachable, time exceeded, source quench, redirect, and parameter problem messages. `p_seprint` prints type name, code, checksum, and type-specific fields such as echo id/sequence, timestamp values, redirect gateway, or parameter pointer.

When global `Cflag` is set, it recomputes and reports checksum mismatches. For ICMP error messages it advances past the unused/gateway/pointer data and sets `m->pr = &ip` to decode the quoted IPv4 packet.

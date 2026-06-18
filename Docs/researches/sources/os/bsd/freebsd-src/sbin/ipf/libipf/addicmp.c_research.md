# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/addicmp.c

This file defines the legacy `icmptypes` string table indexed by ICMP type number up to `MAX_ICMPTYPE`.

It maps common IPv4 ICMP type numbers to short names such as `echorep`, `unreach`, `squench`, `redir`, `echo`, router solicitation/advertisement, time exceeded, parameter problem, timestamp, information, and mask request/reply.

The table is shared by IPFilter parsing/printing code that needs simple ICMP type-name lookup.

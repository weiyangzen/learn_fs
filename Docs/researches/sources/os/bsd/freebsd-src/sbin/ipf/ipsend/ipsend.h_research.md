# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/ipsend.h

This is the shared header for the `ipsend` family.

It documents the purpose: testing what TCP/IP fragments and malformed packets pass packet filters. It includes `ipf.h`, `netinet/tcpip.h`, and `ipt.h`, and declares resolver, ARP, checksum, packet send, option builder, backend, TCP PCB lookup, resend, socket, kernel-copy, and all `ip_test*()` functions.

It defines `KMCPY()` as a wrapper around `kmemcpy()` and ensures `OPT_RAW` exists.

The header couples userland packet-generation code to IPFilter compatibility types and selected kernel TCP/IP structures.

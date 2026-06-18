# File Research: sources/os/bsd/freebsd-src/sbin/setkey/test-pfkey.c

## Summary
Standalone PF_KEY message construction test utility. It builds canned PF_KEY messages for selected message types, sends them to the kernel, and dumps both outgoing and returned messages.

## Main Elements
- Takes a numeric PF_KEY message type.
- Opens a raw PF_KEY v2 socket.
- Builds message buffers in global `m_buf`.
- Provides helpers for SADB message headers, SA, addresses, keys, lifetimes, SPI ranges, identities, sensitivity, and proposals.
- Exercises SAD operations and some SPD operation message forms.
- Uses hard-coded IPv4/IPv6 addresses, SPI, keys, algorithms, and identities.

## Dependencies And Integration
Uses PF_KEY/netipsec structures and `pfkey_sadump()` debug formatting. This is a developer diagnostic program, not part of the normal `setkey` build target.

## Research Notes
The file uses old-style K&R function definitions and fixed global buffers, reflecting its role as a historical/manual PF_KEY exerciser.

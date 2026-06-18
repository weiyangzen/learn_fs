# File Research: sources/os/bsd/freebsd-src/sbin/natd/icmp.c

## Summary
Provides ICMP “fragmentation needed” generation for `natd` when aliasing increases packet size beyond MTU.

## Main Responsibilities
- Avoids responding to non-initial fragments.
- Avoids generating ICMP errors in response to ICMP packets.
- Builds an ICMP unreachable/need-fragment message containing the original IP header plus up to 64 bits of payload.
- Computes ICMP checksum through libalias.
- Builds an IP header from the failed datagram with source/destination swapped.
- Runs the packet through inbound aliasing before sending.
- Sends the ICMP message on a raw ICMP socket.

## Key Function
- `SendNeedFragIcmp()`.

## Research Notes
The function sends only the ICMP payload via `sendto()` after preparing an IP header and aliasing it, matching the divert/raw-socket expectations used by natd.

# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ip_cksum.c

## Role

`ip_cksum.c` provides high-use network checksum helpers for illumos IP-family code: one’s-complement IP checksums over STREAMS mblk chains, SCTP CRC32 checksums, IPv4 header checksums, and IPv6 extension-header length parsing.

## IP Checksum

`ip_cksum()` computes a partial one’s-complement checksum over an `mblk_t` chain. It accepts an initial sum and intentionally does not complement the result, allowing callers to combine partial checksum state.

The function has a fast path for a single aligned mblk and a slow path for chained, odd-length, or odd-address data. The slow path preserves byte ordering across mblk boundaries and handles words split between adjacent buffers.

It also understands `STRUIO_IP` mblks where some data may already have been checksummed. It validates that the requested offset and data pointers still match the precalculated checksum range; otherwise it clears `STRUIO_IP` and falls back to normal checksum calculation.

## Other Helpers

`sctp_cksum()` computes SCTP CRC32 over an mblk chain using `sctp_crc32()`, starting with `0xffffffff` and complementing the final result.

`ip_csum_hdr()` computes and returns the IPv4 header checksum for an `ipha_t`, including optional IPv4 header words. A computed `0xffff` checksum is normalized to zero.

`ip_hdr_length_nexthdr_v6()` walks an IPv6 header and known extension headers contained in the same mblk. It returns the total network header length and optionally a pointer to the next-header field that names the transport header.

## Invariants And Assumptions

- Non-`STRUIO_IP` fast-path data is expected to be 16-bit aligned.
- IPv6 extension-header parsing assumes all IPv6 headers/extensions are in the same mblk.
- Odd-length and odd-address handling depends on endian-specific byte placement.
- `STRUIO_IP` cached checksum state is trusted only when the current mblk spans the expected checksum interval.

## Research Notes

The risk in this file is almost entirely boundary and alignment correctness. Hotspots are split-word handling across `b_cont`, STRUIO partial-checksum invalidation, IPv6 malformed-extension detection, and endian-specific odd-byte accumulation.

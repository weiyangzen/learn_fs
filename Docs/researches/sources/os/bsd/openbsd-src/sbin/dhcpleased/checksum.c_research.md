# File Research: sources/os/bsd/openbsd-src/sbin/dhcpleased/checksum.c

## Purpose
`checksum.c` implements Internet checksum helpers for IPv4 and UDP packet validation/generation.

## Main APIs
- `checksum(uint8_t *buf, uint32_t nbytes, uint32_t sum)`: adds a buffer into an existing 16-bit one's-complement checksum accumulator, handling odd trailing bytes as high-order network-order bytes.
- `wrapsum(uint32_t sum)`: complements, masks, and returns the checksum in network byte order.

## Integration Notes
The engine uses these helpers to validate incoming IP and UDP checksums when BPF/kernel checksum flags do not say they were verified. The frontend uses them when constructing raw IPv4/UDP DHCP packets for BPF transmission.

## Risk Notes
The implementation casts byte buffers to `uint16_t *` for paired-byte reads, matching traditional BSD code but relying on platform tolerance for such access patterns.

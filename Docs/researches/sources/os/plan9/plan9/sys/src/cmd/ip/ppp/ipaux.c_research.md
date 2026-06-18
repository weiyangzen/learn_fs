# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/ipaux.c

Provides checksum helpers for PPP IP/TCP/UDP processing.

Key behavior:
- `ptclbsum` computes a 16-bit partial checksum over a byte buffer, handling alignment and host endianness.
- `ptclcsum` computes an Internet checksum across a chained `Block` list with offset/length.
- `ipcsum` computes an IPv4 header checksum based on the IHL field.

Integration points:
- Used by VJ compression and MPPC debug validation for reconstructed IP packets.
- Depends on `Block` and `BLEN` from `ppp.h`.

Risks and notes:
- Optimized around unaligned/aligned short reads in Plan 9 C; portability needs care.

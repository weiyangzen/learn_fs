# File Research: sources/local-fs/mtd-utils/mcast_image.h

## Purpose
Defines multicast image packet layout and declares the FEC API used for packet recovery.

## Main Data
- `PKT_SIZE` is `2820` bytes of payload per image packet.
- `struct image_pkt_hdr` carries resend flag, total CRC, image block count/size, block CRC/number, packet sequence, packet number/count, current length, and packet CRC.
- `struct image_pkt` combines the header and payload buffer.
- `struct fec_parms` is opaque to callers.

## Dependencies
Uses fixed-width integer types from `<stdint.h>` and corresponds to the implementation in `lib/libfec.c`.

## Risks and Notes
The packet structures are plain C layout with no explicit packing or byte-order conversion in this header, so protocol users must agree on ABI layout and serialization conventions elsewhere.

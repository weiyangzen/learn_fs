# File Research: sources/local-fs/mtd-utils/recv_image.c

## Purpose
Receives a multicast/unicast FEC-protected image stream and writes it to an MTD device or file.

## Key Elements
Opens the target as MTD or fallback file, joins IPv4/IPv6 multicast groups when applicable, receives `image_pkt` datagrams, validates per-packet and whole-image CRC metadata, tracks duplicate/lost packets, writes received packet payloads into flash/file staging locations, decodes missing packets with FEC, verifies block CRCs, erases staged flash blocks, and writes final decoded eraseblocks.

## Dependencies
Uses sockets, multicast APIs, `mcast_image.h` FEC functions, `crc32`, MTD ioctls, and `common.h`.

## Behavior/Risks
Writes to flash while receiving and later rewrites decoded data, so failures can consume spare eraseblocks or abort mid-process. The receiver assumes sender erasesize/block metadata matches the target and exits on many inconsistencies.

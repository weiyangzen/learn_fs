# File Research: sources/local-fs/mtd-utils/serve_image.c

## Purpose
Continuously transmits an image over UDP with FEC redundancy for `recv_image`.

## Key Elements
Parses destination host/port, image path, erasesize, and optional transmit rate. Memory maps the image, validates image size is erasesize-aligned, computes total and per-block CRCs, creates FEC parameters with 50% redundancy, alternates packet order to spread expensive FEC packets, rate-limits sends with `nanosleep`, and loops forever sending packet cycles.

## Dependencies
Uses sockets, `mcast_image.h`, `crc32`, `mmap`, POSIX timing, and network byte-order helpers.

## Behavior/Risks
Runs indefinitely until interrupted. Requires image size to be an exact multiple of erasesize despite having a last-block padding buffer. The rate control is approximate and the lateness adjustment expression appears suspect because it compares `now.tv_usec` against an expression also rooted in `now.tv_usec`.

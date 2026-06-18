# File Research: sources/virtualization/nvme-cli/libnvme/test/ioctl/util.c

## Role

`util.c` provides small support routines for ioctl tests: fatal assertion reporting, byte-buffer comparison, and pseudo-random test data generation.

## Behavior

`fail()` prints a formatted error to stderr and aborts. `cmp()` compares two buffers and, on mismatch, prints a hex dump of actual and expected bytes before aborting. `arbitrary()` fills a buffer with `rand()` bytes. `arbitrary_range()` returns a random value modulo a caller-supplied maximum.

The internal `hexdump()` formats bytes in uppercase hex, separating every 16 bytes with a newline.

## Dependencies

- Standard C stdio, stdarg, stdlib, string, and stdint.
- Paired with `util.h`.

## Filesystem/Storage Relevance

This is generic test infrastructure, but it supports byte-exact validation of NVMe storage command payloads.

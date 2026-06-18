# File Research: sources/virtualization/spdk/lib/util/crc32_ieee.c

This small file implements the IEEE CRC32 public update function.

A constructor initializes a static `spdk_crc32_table` with `SPDK_CRC32_POLYNOMIAL_REFLECT`. `spdk_crc32_ieee_update()` then delegates to `crc32_update()` with that table, the caller buffer/length, and caller-provided CRC seed.

The function does not invert the CRC before or after update; callers are responsible for any protocol-specific initialization/finalization.

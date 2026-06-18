# File Research: sources/virtualization/spdk/lib/util/crc64.c

This file implements NVMe CRC64 using either ISA-L or a table-driven Rocksoft reflected algorithm.

With ISA-L enabled, `spdk_crc64_nvme()` delegates to `crc64_rocksoft_refl()`. Otherwise, it uses a 256-entry precomputed `crc64_rocksoft_refl_table`. `crc64_rocksoft_refl_base()` complements the seed, updates one byte at a time with table lookup indexed by low CRC byte XOR input byte, shifts right by eight, and complements the final value.

`spdk_crc64_nvme()` is the exported function and passes the caller buffer, length, and CRC seed to the selected implementation.

The implementation is stateless. Callers control seed chaining, and non-ISA-L performance is byte-at-a-time rather than sliced or vectorized.

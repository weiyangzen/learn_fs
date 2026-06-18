# File Research: sources/local-fs/udftools/libudffs/crc.c

Implements UDF CRC-16 calculation.

Core behavior:
- Uses a static 256-entry table for the ITU-T V.41 polynomial used by OSTA UDF.
- `udf_crc(data, size, crc)` iterates bytes and updates the supplied CRC seed.

The file also contains optional `TEST` and `GENERATE` compile-time sections:
- `TEST` contains a small hard-coded CRC check.
- `GENERATE` can generate a CRC table for a supplied polynomial.

Key role: descriptor CRC computation for UDF tags and descriptor bodies.

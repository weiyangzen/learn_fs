# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/crc32c.c

This file implements CRC-32C calculation for libgfs2, copied from btrfs-progs/kernel code.

Main behavior:
- Provides `crc32c(seed, data, length)`.
- Defaults to table-driven little-endian CRC-32C via `__crc32c_le()`.
- On `__x86_64__`, can switch to Intel SSE4.2 CRC instructions after `crc32c_optimization_init()`.
- Uses `cpuid` ECX bit 20 to detect hardware CRC32 support.
- Avoids hardware word-sized path for unaligned input buffers and falls back to byte-table CRC.

Integration role:
- Used by journal log-header CRC code in `structures.c`.
- Exposed through `crc32c.h`.

State and ownership:
- Maintains static function pointer `crc_function`.
- Maintains static x86 probe state: `crc32c_probed`, `crc32c_intel_available`.
- Does not allocate memory.

Risk notes:
- x86 hardware path uses inline assembly and casts input to `unsigned long *`; alignment check in `crc32c()` is important.
- Probe state is global and not synchronized, though benign for typical single-threaded tool use.
- CRC semantics must remain compatible with GFS2 on-disk journal checksums.

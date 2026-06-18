<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/crc32b.cpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/lib/crc32b.cpp

Purpose: This file implements table-driven CRC-32B checksum calculation.

Important functions and flow: `crc32b_start` returns the initial `0xFFFFFFFF` seed. `crc32b_continue` iterates each input byte, updates the CRC using `CRC32BTABLE[(crc ^ byte) & 0xFF] ^ (crc >> 8)`, and allows incremental updates. `crc32b_finish` xor-finalizes with `0xFFFFFFFF`. `crc32b` performs the start/continue/finish sequence for one buffer.

State and integration: the 256-entry lookup table is static const data; functions keep all computation in local variables. The C ABI is declared by `crc32b.h`.

Risks and test signals: `crc32b_t` and length are unsigned int, limiting single-call length on platforms where unsigned int is 32-bit. `char` signedness is masked after xor, so ordinary byte input remains stable. Tests should compare known vectors such as empty string and `123456789`, and verify chunked `continue` equals one-shot `crc32b`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/crc32b.cpp -->

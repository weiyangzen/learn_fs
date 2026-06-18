<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/crc32b.h -->
# sources/user-network-fs/mergerfs/vendored/libfuse/lib/crc32b.h

Purpose: This header declares the C ABI for CRC-32B helpers.

Important APIs: `crc32b_t` is `unsigned int`. `crc32b_start`, `crc32b_continue`, and `crc32b_finish` support streaming checksums, while `crc32b` computes a one-shot checksum over a buffer and length.

State and integration: functions own no persistent state; streaming state is the CRC value carried by the caller. The header is C++ compatible through `extern "C"`.

Risks and test signals: callers must pass the prior intermediate CRC to `crc32b_continue`, not the finalized value unless intentionally starting a new stream. Tests should compile from C and C++ and verify known checksum vectors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/crc32b.h -->

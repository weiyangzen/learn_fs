# File Research: sources/virtualization/spdk/lib/accel/accel_sw.c

`accel_sw.c` implements the built-in software accelerator module. It registers an accel module named `software` with fallback support for all framework opcodes: copy, fill, dualcast, compare, CRC32C, copy+CRC32C, compression/decompression, encryption/decryption, XOR, DIF, and DIX.

The module uses per-channel state for optional ISA-L deflate/inflate state, optional LZ4 streams, a completion poller, and a queue of tasks pending completion. Operations execute synchronously inside `sw_accel_submit_tasks()`, but completions are queued to a poller so callbacks are not invoked inline with submission.

Basic memory operations are straightforward: copy uses `spdk_ioviter`, compare walks paired iovecs and returns `-EILSEQ` on mismatch, fill requires a single destination iovec, dualcast requires single source and two single destinations, CRC32C uses SPDK CRC helpers, and XOR uses `spdk_xor_gen()`.

Compression supports DEFLATE via ISA-L when `SPDK_CONFIG_ISAL` is enabled and LZ4 when `SPDK_CONFIG_HAVE_LZ4` is enabled. The software module advertises supported algorithms based on build flags and exposes compression level ranges. Without the required libraries, relevant operations return errors rather than silently doing nothing.

AES-XTS crypto support depends on `SPDK_CONFIG_ISAL_CRYPTO`. Key initialization installs function pointers for 128-bit or 256-bit XTS encrypt/decrypt routines. Runtime crypto walks source and destination iovec lists, processes data in logical block-sized units, increments the IV after each full block, supports in-place operation when no destination iovs are present, and enforces equal source/destination total length and block-size alignment.

DIF/DIX operations delegate to SPDK DIF helpers: verify, verify-copy, generate, generate-copy, DIX generate, and DIX verify. The software module reports no buffer alignment requirement through `get_operation_info()`.

Research notes: this file is the guarantee that the accel framework can assign every opcode even without hardware modules. Build-flag conditionals are important for feature availability: an opcode may be supported in the generic sense while a specific compression algorithm or crypto implementation returns `-EINVAL` or `-ENOTSUP` if its library support is absent.

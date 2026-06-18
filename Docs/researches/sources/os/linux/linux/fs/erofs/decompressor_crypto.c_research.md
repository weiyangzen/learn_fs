# File Research: sources/os/linux/linux/fs/erofs/decompressor_crypto.c

Provides optional hardware/crypto API decompression acceleration for EROFS.

Key behavior:
- Wraps the kernel async compression API (`crypto_acomp`) for decompression.
- Builds scatterlists from request input and output pages.
- Fixes compressed input size before submitting the async request.
- Converts crypto decompression errors to `-EIO`.
- Maintains per-algorithm crypto engine lists; currently DEFLATE has a named `qat_deflate` engine entry.
- `z_erofs_crypto_decompress()` locates an enabled engine, allocates missing output pages, and dispatches crypto decompression.
- `z_erofs_crypto_enable_engine()` allocates and enables a matching crypto transform by name.
- Can disable all engines and show enabled engine names.

Important interactions:
- Used opportunistically by DEFLATE for non-partial decoding.
- Protected by `z_erofs_crypto_rwsem`.
- Falls back via `-EOPNOTSUPP` when no engine is enabled.

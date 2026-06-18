# File Research: sources/os/linux/linux-stable/fs/erofs/decompressor_crypto.c

## Summary
Provides optional crypto API based hardware-accelerated decompression support for EROFS.

## Main Responsibilities
- Converts decompression page arrays into scatterlists.
- Submits asynchronous crypto compression requests and waits.
- Maintains configured crypto accelerator transforms.
- Enables, disables, and lists accelerator engines.

## Key APIs
- `z_erofs_crypto_decompress()`
- `z_erofs_crypto_enable_engine()`
- `z_erofs_crypto_disable_all_engines()`
- `z_erofs_crypto_show_engines()`

## Important Behavior
The current engine table advertises `qat_deflate` for DEFLATE. Output holes are filled with short-lived pages before submitting to crypto because the scatterlist destination requires pages.

## Risks
The enable function matches by `strncmp(name, crypto_name, len)`, so caller-provided lengths matter. Accelerator failures are converted to I/O errors in decompression.

# File Research: sources/os/linux/linux-stable/fs/squashfs/xz_wrapper.c

## Summary
Implements the Squashfs XZ decompressor backend.

## Key APIs
- Exports `squashfs_xz_comp_ops`.

## Important Behavior
The optional XZ compressor options carry dictionary size. The parser validates the option length and accepts dictionary sizes of the supported XZ forms; without options it defaults to max(filesystem block size, metadata block size).

Initialization preallocates an XZ decoder with the selected dictionary size. Decompression streams input directly from BIO segments into `xz_dec_run()` and streams output through the page actor.

`alloc_buffer = 1`, so direct actors can provide a temporary page buffer when a page-cache target is absent.

## Risks
The decompressor requires `XZ_STREAM_END`; running out of BIO input early is treated as corruption. Dictionary validation is necessary to avoid invalid preallocation sizes.

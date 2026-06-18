# File Research: sources/local-fs/squashfs-tools/squashfs-tools/zstd_wrapper.h

## Purpose

`zstd_wrapper.h` defines the stored compressor-option structure and endian-conversion helper used by `zstd_wrapper.c`.

It is guarded by `ZSTD_WRAPPER_H`.

## Includes

The header includes:

- `endian_compat.h`

That provides byte-order detection and endian helper declarations used by the Squashfs tools.

## Endian Handling

On big-endian hosts, the header declares:

- `inswap_le16(unsigned short)`
- `inswap_le32(unsigned int)`

and defines `SQUASHFS_INSWAP_COMP_OPTS(s)` to byte-swap:

- `(s)->compression_level`

using `inswap_le32()`.

On little-endian hosts, `SQUASHFS_INSWAP_COMP_OPTS(s)` is a no-op.

The macro is used both when writing compressor options and when reading/displaying them. Because it swaps in place, callers must avoid accidentally applying it twice to the same already-swapped structure unless they intend to reverse the conversion.

## Constants

The header defines:

- `ZSTD_DEFAULT_COMPRESSION_LEVEL 15`

This is the Squashfs zstd wrapper default, used by `zstd_wrapper.c` to decide whether options need to be serialized and to reset append-mode defaults when no stored option block exists.

## Stored Option Structure

The header defines:

```c
struct zstd_comp_opts {
	int compression_level;
};
```

This structure is the on-image compressor option payload for zstd when the compression level differs from the Squashfs default.

## Research Notes

The header’s entire behavioral surface is the ABI for zstd compressor options in Squashfs images. Any change to `struct zstd_comp_opts` or the byte-swap macro affects compatibility with stored compressor options and append-mode reconstruction.

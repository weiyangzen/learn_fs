# File Research: sources/local-fs/squashfs-tools/squashfs-tools/compressor.h

Defines the compressor vtable contract.

`struct compressor` fields cover:
- SquashFS compressor ID and display name.
- Whether the compressor is compiled/supported.
- Optional init hook.
- Required compress/uncompress hooks.
- Optional command-line option parsing and postprocessing.
- Optional dump/extract/check/display of on-disk compressor options.
- Optional help and option-arity helpers.

Inline wrappers:
- Provide null-safe defaults for optional hooks.
- Treat missing `extract_options` as accepting only zero-sized option blocks.
- Treat missing `check_options` as success.
- Treat missing `option_args` as no extra args.

Key role: common ABI for gzip, lzo, lz4, xz/zstd/lzma wrappers and callers in mksquashfs/unsquashfs.

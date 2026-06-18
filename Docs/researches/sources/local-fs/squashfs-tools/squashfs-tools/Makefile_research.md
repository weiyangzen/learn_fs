# File Research: sources/local-fs/squashfs-tools/squashfs-tools/Makefile

Top-level build recipe for the SquashFS tools in this subtree. It builds `mksquashfs` plus symlink `sqfstar`, and `unsquashfs` plus symlink `sqfscat`.

Main responsibilities:
- Defines configurable compression support: gzip, xz, lzo, lz4, zstd by default; obsolete lzma variants optional.
- Defines xattr support switches: generic xattr support, OS xattr support, and default xattr behavior.
- Defines reader thread defaults and validates thread counts against `MAX_READER_THREADS`.
- Selects compressor wrapper objects, libraries, and `COMPRESSORS` help text based on enabled options.
- Injects build-time `COMP_DEFAULT`, `VERSION`, `DATE`, and `YEAR` into `CFLAGS`.
- Builds object lists for `mksquashfs` and `unsquashfs`, including feature-gated xattr/compressor objects.
- Installs binaries, symlinks, and generated or prebuilt manpages through `generate-manpages/install-manpages.sh`.

Important dependency behavior:
- `CONFIG=1 make` flips many defaults to command-line-overridable `?=` values and uses different reader-thread defaults.
- `COMP_DEFAULT` must be set and must appear in the selected `COMPRESSORS`.
- `LZMA_XZ_SUPPORT` and `LZMA_SUPPORT` are mutually exclusive.
- At least one compressor must be enabled.

Notable quirks:
- `INSTALL_MANPAGES_DIR` default differs between normal and `CONFIG=1` branches: `/usr/local/share/man/man1` vs `/usr/local/man/man1`.
- Installation script arguments are not shell-quoted, so paths containing spaces are not robust.

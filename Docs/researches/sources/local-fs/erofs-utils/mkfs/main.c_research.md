# File Research: sources/local-fs/erofs-utils/mkfs/main.c

## Scope

This file is the `mkfs.erofs` command-line entry point. It parses options, configures compression/xattr/tar/rebuild/S3/OCI/metabox/blob modes, opens inputs and output image, initializes importer state, builds the source tree, flushes metadata/data, writes the superblock, optionally writes checksums and VMDK descriptors, and cleans up global resources.

## Public And Internal APIs Covered

- User-facing helpers: `usage()`, `version()`, `parse_source_date_epoch()`, and `erofs_show_progs()`.
- Option parsers: `parse_extended_opts()`, `mkfs_apply_zfeature_bits()`, `mkfs_parse_tar_cfg()`, `mkfs_parse_options_cfg()`, compressor parser helpers, numeric parser helpers, and optional S3/OCI parser helpers.
- Source setup: `mkfs_parse_sources()` and `erofs_mkfs_rebuild_load_trees()`.
- Defaults and summaries: `erofs_mkfs_default_options()` and `erofs_mkfs_showsummaries()`.
- Program control: `main()`.

## Control Flow And Behavior

- Static long options expose core mkfs controls: block size, verbosity, xattrs, compression, pcluster sizes, metadata compression, timestamps, UUID, exclusion rules, SELinux labels, uid/gid mapping, tar/index modes, blob devices, incremental/rebuild modes, metazone/metabox controls, xattr prefixes, VMDK output, and optional S3/OCI/gzip/lzma/gzran/multithreaded features.
- `usage()` prints supported compressors dynamically, including level/dictionary ranges and LZMA advanced options.
- Extended options toggle inode format forcing, superblock CRC disabling, data inlining, chunk format forcing, xattr name filters, plain xattr prefixes, ztailpacking, fragments/all-fragments, dedupe, fragment dedupe, 48-bit layout, and dot omission.
- Compression option parsing supports colon-separated algorithm sets, per-algorithm `level=`, `dictsize=`, old numeric level syntax, and extra compressor-specific options.
- Source parsing chooses local directory, rebuild-from-image, tar stream/file, S3, or OCI. Rebuild mode opens one or more existing EROFS images as sources and assigns extra-device ids.
- `mkfs_parse_options_cfg()` validates option interactions: blobdev requires chunksize, blobdev cannot currently use block-map chunk format, chunksize must be a power of two and at least block size, pcluster sizes must be block-size multiples, metabox requires valid pcluster sizing, and tar index mode may force 512-byte blocks.
- `SOURCE_DATE_EPOCH` switches build-time behavior to reproducible-build clamping if valid.
- Main initialization calls global setup, importer preset/defaults, option parsing, output device open, optional Android fs config load, config display, tar/rebuild/OCI block-size adjustment, and clean or incremental filesystem initialization.
- Clean builds generate a UUID unless the user supplied one. Incremental builds load an existing superblock and append through `erofs_mkfs_load_fs()`.
- Disk buffers are initialized for full tar, S3, and OCI imports that need staged file payloads. Compression hints and importer state are then initialized.
- Dedupe setup selects compressed-data dedupe when compression is active, or falls back to chunk-based data dedupe when forced without compression.
- Blob/device-table setup occurs for tar index mode, explicit blob devices, rebuild blob-index mode, or extra-device outputs.
- Local-directory sources pre-scan shared xattrs before root inode creation. All source modes flush configured xattr name prefixes before tree import.
- Tree building dispatches by source: tar records are parsed until end-of-archive, rebuild sources load existing trees, S3 builds from object-store metadata/data, and OCI builds from remote image/layers. Unsupported incremental/reserved-space combinations return `-EOPNOTSUPP`.
- After import, `erofs_importer_load_tree()` finalizes the tree, blob/index metadata is dumped when needed, all importer outputs are flushed, root is dropped, the superblock is written, the device is resized, optional superblock checksum is enabled, and optional VMDK descriptor is generated.
- Exit cleanup drops root, dedupe, blocklist output, compression hints, exclude rules, blob state, xattr prefixes, rebuild sources, disk buffers, tar streams/dump fds/zinfo export, importer state, superblock state, device fd, and global library state.

## State And Data Structures

- `mkfscfg` stores compression parameter sets, inline-xattr tolerance, inode metazone flag, build timestamp, and total compression configs.
- Global/static mode state includes pcluster sizes, tarfile state, incremental flag, metabox algorithm id, source mode, rebuild source list/count, fixed UUID, dsunit, tar decoder, VMDK output file, zinfo output file, optional S3/OCI configs, and data import mode.
- `erofs_importer_params` carries per-build behavior into the shared importer pipeline.
- The program mutates global `cfg` and `g_sbi` throughout option parsing and build execution.

## Dependencies

- Links against `liberofs.la` and uses importer, inode, tar, xattr, dedupe, exclude, block-list, compression hints, blobchunk, compressor, gzran, metabox, OCI, private rebuild, S3, UUID, diskbuf, and superblock/device helpers.
- Optional compile-time dependencies include libselinux, zlib, liblzma, multithreading, Android fs config, S3, and OCI support.

## Risks And Invariants

- Many options mutate global state during parsing; validation order matters because later checks assume `mkfs_blkszbits`, chunk bits, feature bits, and source mode are settled.
- Tar index mode without a mapfile forces 512-byte blocks and creates an extra device entry for the tar source; this must be coordinated with superblock/device-table writing.
- Rebuild blob-index mode assumes each source image has either no extra device or exactly one extra device; mismatches are rejected.
- Cleanup is centralized under `exit:` and must tolerate partially initialized subsystems.
- `--quiet` lowers output and disables progress after parsing; errors still propagate through final formatting failure reporting.

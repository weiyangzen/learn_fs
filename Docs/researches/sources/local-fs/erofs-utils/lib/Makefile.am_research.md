# File Research: sources/local-fs/erofs-utils/lib/Makefile.am

## Purpose
Automake build file for the internal `liberofs.la` library and optional test programs.

## Key Details
- Defines `noinst_LTLIBRARIES = liberofs.la`.
- Lists installed-in-tree headers under `noinst_HEADERS`, including public `include/erofs/*` headers and internal `lib/liberofs_*` headers.
- Core sources include config, I/O, cache, superblock, inode, xattr, data mapping, compression, decompression, zmap, fragments, dedupe, tar, rebuild, diskbuf, blobchunk, metabox, importer, base64, and more.
- Conditional sources:
  - LZ4/LZ4HC compressors.
  - liblzma compressor.
  - libdeflate compressor.
  - libzstd compressor.
  - bundled `xxhash.c` fallback when system xxhash is unavailable.
  - S3 remote support.
  - workqueue for multithreaded EROFS compression.
  - Linux NBD backend.
  - OCI/docker config remotes and gzran support.
- Adds dependency flags/libs for uuid, selinux, lz4, lzma, zlib, libdeflate, zstd, QPL, curl, OpenSSL, libxml2, libnl3, json-c, and pthread as configured.

## Interactions
- This build file determines which compression and backend implementations are compiled and therefore which algorithms/backends `mkfs`, `fsck`, and other tools can use.
- `fsck/Makefile.am` links directly against this library.

## Notes
The file is the main feature-gating point for `liberofs`.

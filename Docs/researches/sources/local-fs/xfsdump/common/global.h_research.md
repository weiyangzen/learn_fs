# File Research: sources/local-fs/xfsdump/common/global.h

## Summary
Defines the fixed first-page global media-file header and declares helpers for allocation, checksum, and version validation.

## Main Contents
`global_hdr_t` is exactly one page (`GLOBAL_HDR_SZ = PGSZ`) and begins every media file. It contains:
- xfsdump magic `xFSdump0`.
- Header version, currently `GLOBAL_HDR_VERSION_3`.
- Header checksum.
- Dump timestamp.
- Host id.
- Dump session UUID.
- Hostname.
- Dump label.
- `gh_upper`, reserved for upper-layer headers.

Version notes:
- Version 1 adds extended file attribute dumping.
- Version 2 adds hole encoding and inventory format changes.
- Version 3 uses the full 32-bit inode generation number in directory entry headers.

## Exposed APIs
- `global_hdr_alloc()`.
- `global_hdr_free()`.
- `global_hdr_checksum_set()`.
- `global_hdr_checksum_check()`.
- `global_version_check()`.

## Risks
The layout is on-media format. Field sizes, offsets, and `GLOBAL_HDR_SZ` are compatibility-sensitive and are assumed by drive backends.

`gh_upper` embeds higher-layer headers by convention, so users must preserve layering and size assumptions.

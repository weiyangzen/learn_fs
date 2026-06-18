# File Research: sources/local-fs/xfsprogs/mkfs/proto.h

## Purpose
Declares the mkfs protofile/directory population interface used by `xfs_mkfs.c`.

## Key Elements
Defines `enum proto_source_type` with `PROTO_SRC_NONE`, `PROTO_SRC_PROTOFILE`, and `PROTO_SRC_DIR`, plus `struct proto_source` carrying source type and associated string data.

Exports `setup_proto`, `parse_proto`, and `res_failed`.

## Dependencies
Uses `struct xfs_mount` and `struct fsxattr` from the surrounding xfsprogs/libxfs headers included by callers.

## Behavior/Risks
The API abstracts protofile and directory inputs behind a single `proto_source`, letting the mkfs main path defer root population until after devices, AG headers, and free-space metadata are initialized.

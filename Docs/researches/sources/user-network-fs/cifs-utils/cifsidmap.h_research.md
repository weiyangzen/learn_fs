<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cifsidmap.h -->
# sources/user-network-fs/cifs-utils/cifsidmap.h

## Purpose

`cifsidmap.h` defines the binary SID and Unix-ID mapping structures and plugin ABI that CIFS idmap helpers and plugins share.

## Important APIs, Types, and Functions

The header defines `NUM_AUTHS`, `SID_MAX_SUB_AUTHORITIES`, packed `struct cifs_sid`, mapping type constants `CIFS_UXID_TYPE_UNKNOWN`, `CIFS_UXID_TYPE_UID`, `CIFS_UXID_TYPE_GID`, `CIFS_UXID_TYPE_BOTH`, packed `struct cifs_uxid`, and plugin symbols `cifs_idmap_init_plugin`, `cifs_idmap_exit_plugin`, `cifs_idmap_sid_to_str`, `cifs_idmap_str_to_sid`, `cifs_idmap_sids_to_ids`, and `cifs_idmap_ids_to_sids`.

## Control Flow

Helpers load plugin symbols dynamically and call initialization to obtain an opaque handle. Conversion calls operate on preallocated arrays, with per-element unknown/revision-zero markers for partial failures.

## State and Persistence Behavior

The structures are transient binary payloads for kernel key instantiation, ACL xattr parsing, and plugin conversion. Plugin state is opaque and owned by the plugin handle.

## Dependencies and Integration Points

It requires `uid_t`, `gid_t`, `size_t`, and fixed-width integer types from system headers. It is consumed by `cifs.idmap.c`, `idmap_plugin.c`, `idmapwb.c`, `getcifsacl.c`, and ACL utilities.

## Risks and Edge Cases

The SID subauthority array is always stored little-endian in `struct cifs_sid`, while plugins may use host-endian representations. The ABI is symbol-name based; missing functions become runtime failures. The packed layout is compatibility-sensitive.

## Test Signals

Tests should validate struct sizes/layouts, max subauthority handling, partial mapping semantics, BOTH-type behavior, and raw key payload compatibility with the kernel CIFS client.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cifsidmap.h -->

# File Research: sources/local-fs/ocfs2-tools/include/ocfs2/jbd2.h

## Purpose

Carries the subset of Linux JBD2 journal on-disk definitions required by OCFS2 userspace tools.

## Main Contents

- Defines JBD2 magic number and descriptor block types.
- `journal_header_t` standard big-endian journal block header.
- Checksum type constants and commit header with checksum and commit timestamp fields.
- `journal_block_tag_t` for descriptor tags, with 32-bit and 64-bit tag size macros.
- Revoke header and descriptor tag flag definitions.
- `journal_superblock_t` with static journal information, dynamic log state, error code, feature flags, UUID/users, transaction limits, padding, and user IDs.
- Feature testing macros and known feature masks.

## Dependencies and Integration

- Included by `include/ocfs2/ocfs2.h`.
- Used by libocfs2 journal initialization, feature update, tag parsing, and byte-swapping APIs.

## Research Notes

- JBD2 structures use big-endian fields, unlike most OCFS2 disk metadata.
- Tag size depends on the journal 64-bit incompat feature and must not be inferred from raw `sizeof` in all cases.

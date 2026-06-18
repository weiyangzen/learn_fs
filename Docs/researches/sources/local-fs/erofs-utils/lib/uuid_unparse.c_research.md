# File Research: sources/local-fs/erofs-utils/lib/uuid_unparse.c

## Scope

This small file formats a 16-byte UUID into lowercase canonical text.

## Public And Internal APIs Covered

- `erofs_uuid_unparse_lower()` writes a 36-character hyphenated UUID string plus trailing NUL into the caller-provided output buffer.

## Control Flow And Behavior

- Uses `sprintf()` with eight 16-bit groups assembled from adjacent bytes and hyphens in the `8-4-4-4-12` UUID layout.

## Dependencies

- Standard `stdio.h`, EROFS config, and UUID helper declarations.

## Risks And Invariants

- The caller must provide enough storage for 37 bytes.
- Byte grouping must match `erofs_uuid_parse()` and superblock UUID display expectations.

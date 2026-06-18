# sources/object-store/rustfs/crates/ecstore/src/data_movement.rs

## Purpose
This file implements object data movement helpers for moving objects between pools/sets while preserving object identity and metadata. It supports multipart and single-part movement through normal object-store APIs.

## Important APIs, types, and functions
`IndexedDataMovementReader` wraps a reader plus optional compressed index and implements hash/index traits. Public helpers include `decode_part_index`, `put_obj_reader_from_chunk`, and multipart abort flag helpers. `migrate_object` is the central operation. Private helpers create data-movement `ObjectOptions`, wrap stage errors, compare source and target `ObjectInfo`, and decide overwrite-resume completion.

## Control flow
Multipart movement creates a destination upload, reads each source part fully into memory, rebuilds a hash reader with actual size and optional index, uploads each part preserving ETag, and completes with source version/modtime/ETag options. On completion overwrite errors, it checks whether the destination pool already has an equivalent object and treats that as success. Failures before completion abort the multipart upload unless completion cleared the abort flag. Single-part movement streams through `put_object` with preserved metadata.

## State and persistence behavior
No durable state is owned here, but object data is written through `ECStore`. `ObjectOptions` mark data movement, source pool, versioning/version ID, user metadata, mod time, and preserve ETag. Abort state is a per-operation `AtomicBool`.

## Dependencies and integration points
It depends on `ECStore`, object and multipart APIs, `ObjectInfo`, `ObjectOptions`, `PutObjReader`, `rustfs_rio` hash/index traits, `bytes`, `sha2`, `hex_simd`, and directory object encoding. Rebalance/migration callers invoke `migrate_object`.

## Risks and edge cases
Multipart parts are buffered fully in memory. Invalid indexes are silently dropped. Resume success requires strict metadata equivalence and can fail if fields are normalized differently. Single-part movement lacks overwrite-resume equivalence handling. Abort failure wraps the primary failure with cleanup context.

## Test signals
Tests cover abort flags, error messages, overwrite gating, index decoding, option metadata preservation, equivalence rules, and resume-result handling. Full `migrate_object` integration, large-part memory behavior, and live abort cleanup are not covered here.

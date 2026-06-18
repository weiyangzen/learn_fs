# sources/user-network-fs/s3fs-fuse/src/types.h

## Purpose
Defines shared lightweight types and enums for S3 metadata, ACLs, encryption/signature settings, multipart upload bookkeeping, directory rename bookkeeping, MIME maps, and object-kind classification.

## Important APIs, Types, And Control Flow
`xattrs_t` maps xattr names to values. `acl_t` plus `str(acl_t)`/`to_acl` converts S3 canned ACLs. `sse_type_t` and `signature_type_t` encode option choices. Multipart support uses `etagpair`, pointer-stable `etaglist_t`, `petagpool`, `filepart`, `filepart_list_t`, `untreatedpart`, `untreated_list_t`, `mp_part`, `mp_part_list_t`, and `total_mp_part_list`. `mvnode` describes rename operations. `mimes_t` is a case-insensitive map with transparent lookup. `objtype_t` models files, symlinks, several directory representations, and negative cache entries with helper predicates and `STR_OBJTYPE`.

## State And Persistence
Types are mostly value containers. Destructors call `clear`, which resets owned strings and pointers but does not close file descriptors in `filepart`; fd ownership is external. Pointer stability is explicitly required for etag lists/pools because `filepart` stores `etagpair*`.

## Dependencies And Integration Points
Includes standard containers and optional xattr system headers based on configure macros. This header is widely shared by metadata, cache, multipart upload, object classification, MIME, and rename code.

## Risks And Test Signals
`to_acl` assumes non-null input. `filepart` constructor ignores its `is_uploaded` argument and leaves `uploaded` default false, which may be intentional or a bug. Raw fd and pointer fields rely on external ownership. Object type equivalence treats all directory encodings as same, so callers needing exact representation must avoid `IS_SAME_OBJ`. Integration tests for ACL-like metadata, xattrs, multipart upload/copy/mix, implicit directories, and rename behavior exercise these contracts indirectly.

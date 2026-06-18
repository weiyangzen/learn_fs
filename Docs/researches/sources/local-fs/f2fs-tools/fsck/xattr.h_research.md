# File Research: sources/local-fs/f2fs-tools/fsck/xattr.h

Defines userspace F2FS xattr, fscrypt context, fsverity location, and POSIX ACL on-disk structures and helper macros.

Key contents:
- `struct f2fs_xattr_header` and `struct f2fs_xattr_entry` describe F2FS xattr storage.
- Defines fscrypt v1/v2 context structures, expected sizes, and `fscrypt_context_size()`.
- Defines `struct fsverity_descriptor_location`.
- Defines POSIX ACL structures and `f2fs_acl_count()` for validating ACL entry count from serialized size.
- Provides fallback `XATTR_*` prefix and flag definitions when system headers do not provide them.
- Defines F2FS xattr indexes for user, POSIX ACL, trusted, security, encryption, and verity namespaces.
- Provides xattr iteration/alignment macros: `XATTR_ALIGN`, `ENTRY_SIZE`, `XATTR_NEXT_ENTRY`, `XATTR_FIRST_ENTRY`, `list_for_each_xattr`.
- Defines inline/external xattr capacity helpers such as `VALID_XATTR_BLOCK_SIZE`, `XATTR_SIZE()`, `MIN_OFFSET`, `MAX_VALUE_LEN`, and `MAX_INLINE_XATTR_SIZE`.

Important dependencies:
- Includes `f2fs.h`, so it relies on inode layout helpers, `inline_xattr_size()`, block size, node footer size, and endian helpers.
- Used by `xattr.c` and fsck/sload xattr-related paths.

Behavioral notes:
- `IS_XATTR_LAST_ENTRY(entry)` treats four zero bytes as the list terminator.
- Several structures are protected with `static_assert` to maintain on-disk ABI sizes.

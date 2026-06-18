# File Research: sources/local-fs/xfsprogs/db/hash.c

## Purpose
Implements name hash inspection and collision-name generation for XFS directory, attribute, and parent-pointer hashes.

## Main Interfaces
- Registers `hash` and `hashcoll` through `hash_init()`.
- `hash` prints attr hashes by default, directory hashes with `-d`, or parent-pointer hashes with `-p parent_ino`.
- `hashcoll` generates obfuscated same-hash variants, optionally as xattrs (`-a`), from stdin (`-i`), with count (`-n`), seed (`-s`), or direct creation under a path (`-p`).

## Control Flow
`hash_f()` converts each input string into an `xfs_name` and calls the matching libxfs hash function. `hashcoll_f()` opens an optional directory or file, reads one or more source names, and delegates to `collide_dirents` or `collide_xattrs`. Collision generation uses `obfuscate_name()` and `find_alternate()` while a duplicate table prevents repeated generated names when not using the filesystem itself as the duplicate detector.

## Dependencies
Depends on libxfs dir/attr/parent hash functions, the obfuscation helpers, crc32c for duplicate table buckets, POSIX `openat/linkat`, and Linux xattr APIs.

## Risks And Invariants
- Directory collision generation with `-p` creates a real file and hardlinks; xattr mode creates real `user.*` attributes.
- Duplicate tracking is skipped when only one name is requested or when the target filesystem object is used to detect duplicates.
- Generated names are printed NUL-separated, which is deliberate for scripting.

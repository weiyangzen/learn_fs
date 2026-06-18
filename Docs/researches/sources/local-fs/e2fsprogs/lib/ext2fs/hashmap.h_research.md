# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/hashmap.h

## Role

Declares the ext2fs hashmap API and public iterator entry layout.

## Main Contents

- Forward declaration for `struct ext2fs_hashmap`.
- Entry struct with `data`, key pointer/length, bucket `next`, and insertion-order links.
- API declarations for create, add, lookup, ordered iteration, delete, free, and DJB2 hash.

## Dependencies

Includes `stdlib.h` and `stdint.h`; defines `__GNUC_PREREQ` fallback for pedantic diagnostics in the implementation.

## Risks / Notes

- Declares `ext2fs_hashmap_del()`, but the implementation file in this group does not define it.
- Public entry layout exposes internals to iterator users.

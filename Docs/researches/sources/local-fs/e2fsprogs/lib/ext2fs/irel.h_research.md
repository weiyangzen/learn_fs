# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/irel.h

## Role

Defines the inode relocation table abstraction used to map old/new/original inode numbers and track references that must be updated.

## Main Contents

- `ext2_inode_reference`: block plus offset of an inode reference.
- `ext2_inode_relocate_entry`: new inode, original inode, flags, and max reference count.
- `ext2_inode_relocation_table`: virtual table with put/get/get-by-orig, iteration, reference iteration, move, delete, and free callbacks.
- Macro wrappers call through the function table.
- Factory declaration for the memory-array implementation.

## Dependencies

Depends on ext2fs scalar types and `errcode_t`.

## Risks / Notes

- Reference iteration state lives in the `ext2_irel` object, so only one reference iteration can be active at a time.
- Implementations must keep relocation entries and reference arrays synchronized when moving/deleting entries.

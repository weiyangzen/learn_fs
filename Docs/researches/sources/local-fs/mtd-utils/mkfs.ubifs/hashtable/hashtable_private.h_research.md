# File Research: sources/local-fs/mtd-utils/mkfs.ubifs/hashtable/hashtable_private.h

## Purpose
Defines the private storage layout for the bundled hashtable implementation.

## Main Definitions
- `struct entry` stores key, value, cached mixed hash, and next-chain pointer.
- `struct hashtable` stores bucket count, bucket array, entry count, load limit, prime-table index, and hash/equality callbacks.
- Declares `hash()` for internal and iterator use.
- `indexFor()` maps a hash to a bucket using modulo.
- `freekey()` currently maps to `free()`.

## Dependencies
Includes the public hashtable header and assumes libc `free()` is visible through implementation includes.

## Risks and Notes
The `freekey()` macro makes heap allocation of keys part of the table contract. Static or borrowed key strings cannot safely be inserted unless `freekey` is changed.

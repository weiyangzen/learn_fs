# File Research: sources/local-fs/mtd-utils/mkfs.ubifs/devtable.c

## Purpose
Parses mkfs.ubifs device table files and stores requested filesystem entries or attribute overrides for later use while walking the host root.

## Main Entry Points
- `parse_devtable()` reads and validates a device table file, creating the top-level path hash table.
- `devtbl_find_path()` and `devtbl_find_name()` look up pending table entries by parent path and basename.
- `override_attributes()` applies UID, GID, and mode overrides to an existing host entry and removes the consumed table entry.
- `first_name_htbl_element()` and `next_name_htbl_element()` iterate remaining entries under a path so mkfs.ubifs can synthesize nodes not present on the host.
- `free_devtable_info()` destroys all nested hash tables.

## Data Model
`path_htbl` maps a directory path such as `/dev` to a `struct path_htbl_element`. Each path element owns a second hashtable of `struct name_htbl_element` objects keyed by basename. Counted device-table entries expand names like `tty0`, `tty1`, etc. with calculated device minor numbers.

## Parsing Rules
Entries must use absolute, normalized paths without trailing slash, `//`, `.`, or `..`. Supported types are directory, regular file, FIFO, character device, and block device. Existing host special files cannot also be created from the table; regular files/directories must match type if overridden.

## Dependencies
Uses mkfs.ubifs types from `mkfs.ubifs.h` and the bundled Christopher Clark hashtable implementation.

## Risks and Notes
The parser stores allocated strings as hashtable keys and also as element names, relying on the hashtable's key-freeing behavior for cleanup. Several duplicate/error paths return immediately after allocation or lookup failures and can leak small intermediate allocations before process exit.

# File Research: sources/local-fs/squashfs-tools/squashfs-tools/unsquash-12.c

This helper file provides shared functionality for the Squashfs 1.x and 2.x readers.

Key content:
- Includes `merge_sort.h`.
- Instantiates `SORT(sort_directory, dir_ent, name, next)`.

Behavior:
- Generates a linked-list merge sort function named `sort_directory`.
- Sorts `struct dir_ent` nodes by their `name` field using the `next` pointer.
- Used by v1 and selected v2 directory handling before calling `check_directory`.

Importance:
- Older filesystem versions may require sorting before duplicate-name validation.
- Keeping this helper separate avoids duplicating the macro instantiation in both legacy readers.

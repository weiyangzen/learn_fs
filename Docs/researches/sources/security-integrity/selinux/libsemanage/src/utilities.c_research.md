# sources/security-integrity/selinux/libsemanage/src/utilities.c

## Purpose
General helper library for string parsing, simple linked lists, file slurping, robust writes, and basename.

## APIs and control flow
`semanage_findval()` scans a file for a variable prefix and returns text after a delimiter. Split/prefix/rtrim/count helpers support configuration parsing. List helpers push unique strings, pop, destroy, find, and qsort nodes. `semanage_str_replace()` allocates a replacement string with optional occurrence limit. `semanage_slurp_file_filter()` stores accepted lines without duplicating after getline ownership transfer. `write_full()` retries short/EINTR writes.

## Dependencies and risks
Uses libc I/O, asserts, and errno. `semanage_list_sort()` dereferences `(*l)->next` when `*l` is NULL, so callers must pass a non-empty list. `semanage_str_replace()` assumes non-NULL inputs and can underflow size arithmetic if replacement is shorter without careful unsigned reasoning.

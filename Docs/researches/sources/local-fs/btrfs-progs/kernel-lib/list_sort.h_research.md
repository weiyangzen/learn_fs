# File Research: sources/local-fs/btrfs-progs/kernel-lib/list_sort.h

## Purpose
Declaration header for the list sort helper.

## Contents
- Include guard `_LINUX_LIST_SORT_H`.
- Forward declares `struct list_head`.
- Declares `list_sort()`.

## Risks
No logic. The comparator contract is documented in `list_sort.c`, not this header.

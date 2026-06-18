# File Research: sources/local-fs/btrfs-progs/kernel-lib/list_sort.c

## Purpose
Stable merge sort for `struct list_head` lists, adapted from Linux `lib/list_sort.c`.

## Key Interface
- `list_sort(void *priv, struct list_head *head, int (*cmp)(...))`.

## Implementation
- Converts the circular doubly linked list into null-terminated forward lists.
- Accumulates sorted partial lists in `part[MAX_LIST_LENGTH_BITS + 1]`.
- Uses stable merge behavior: equal elements choose the left input first.
- Final merge restores `prev` links and the circular sentinel head.

## Dependencies
Includes `kerncompat.h`, `stdio.h`, `string.h`, `kernel-lib/list_sort.h`, and `kernel-lib/list.h`.

## Risks
- Lists longer than the fixed partial-list capacity trigger a warning and reduce efficiency, but still continue.
- During final back-link restoration, `cmp(priv, tail->next, tail->next)` is called intentionally; comparators must tolerate identical arguments.

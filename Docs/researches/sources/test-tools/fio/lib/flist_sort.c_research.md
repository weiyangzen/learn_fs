# sources/test-tools/fio/lib/flist_sort.c

Purpose: stable merge-sort implementation for fio intrusive doubly-linked lists.

Important APIs/functions: exported `flist_sort`; static `merge` and `merge_and_restore_back_links`. The comparator receives caller private data and two `flist_head` entries.

Control flow: the circular doubly-linked list is temporarily converted into null-terminated singly-linked runs. The algorithm accumulates sorted partial lists by binary carry merging, then merges the last parts while restoring `prev` links and circular head/tail links.

State/persistence: mutates only the provided list links. No allocation occurs; maximum efficient list length is bounded by `MAX_LIST_LENGTH_BITS`, with a log warning if exceeded.

Dependencies/integration: depends on fio `flist.h` and `log.h`. Comparator callbacks may do scheduling or side effects; the final restoration loop deliberately calls `cmp` during long tail processing.

Risks/test signals: link corruption is the main risk. Tests should cover empty, one-element, already-sorted, reverse-sorted, duplicate-key stability, and very long lists near the warning threshold.

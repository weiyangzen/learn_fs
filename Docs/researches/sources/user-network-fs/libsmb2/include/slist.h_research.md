# sources/user-network-fs/libsmb2/include/slist.h

## Purpose
`slist.h` defines lightweight singly linked list macros used internally by libsmb2.

## Important APIs, Types, and Functions
`SMB2_LIST_ADD(list, item)` prepends an item. `SMB2_LIST_ADD_END(list, item)` appends by walking the list. `SMB2_LIST_REMOVE(list, item)` unlinks a matching item. `SMB2_LIST_LENGTH(list, length)` counts elements. Each macro assumes list elements have a `next` member.

## Control Flow
The append, remove, and length macros temporarily advance `*list` while walking and restore the original head from a local `void *head`. `SMB2_LIST_ADD` updates the item's `next` and then updates the head.

## State and Persistence Behavior
The macros mutate caller-owned in-memory list links only. They allocate and free nothing.

## Dependencies and Integration Points
It is a non-installed internal helper used by list-managing implementation code such as context, queue, or directory-entry tracking. It has no external library dependencies.

## Risks and Edge Cases
Macros evaluate arguments multiple times and are not type-safe. The `void *head` restoration relies on compatible pointer assignment. `SMB2_LIST_REMOVE` does not clear the removed item's `next`, which can surprise callers that reuse removed nodes.

## Test Signals
Unit-test prepend, append to empty/non-empty lists, remove head/middle/tail/missing items, length on empty and populated lists, and repeated remove/reinsert behavior.

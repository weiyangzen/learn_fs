# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_attr_list.c

## Purpose

Implements extended-attribute listing for shortform, leaf, and node-format attr forks.

## Main Responsibilities

- Lists shortform attrs directly or sorted by hash when output buffers are too small.
- Walks attr btrees from cursor hash to the correct leaf.
- Validates cursor-provided leaf blocks and falls back to root lookup if needed.
- Lists leaf entries while preserving cursor progress.
- Filters incomplete entries unless explicitly allowed.
- Dispatches listing by attr fork format.

## Shortform Listing

Shortform entries are not stored in hash order. If all entries fit in the output buffer from a reset cursor, the code emits them directly. Otherwise it builds a temporary array of hash/name/value records, sorts by hash and entry number, and resumes from the cursor.

## Node/Leaf Listing

Node listing descends by hash value through da nodes, validates headers and levels, then walks leaf forward links. Leaf listing re-synchronizes duplicate hashes using `cursor->offset` and `context->dupcnt`.

## Important Invariants

- Cursor validation is defensive; suspicious block pointers force a new tree lookup.
- Tree depth and level ordering are checked to detect corruption.
- Attribute names and namespaces are validated before callback emission.
- Corruption marks the attr fork sick.

## Dependencies

- Attr shortform and leaf helpers.
- DA btree node read/check helpers.
- XFS attr hash and namespace validation.
- Caller-provided `put_listent` callback.

## Research Notes

This file is the attr-list cursor engine. Its core challenge is stable resumption across hash-sorted formats and unsorted shortform storage.

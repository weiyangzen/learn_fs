# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_attr_item.c

## Purpose

Implements logged extended-attribute deferred operation intents and done items: ATTRI and ATTRD. These support replayable xattr updates, removals, replacements, and parent-pointer operations.

## Main Responsibilities

- Manages ATTRI and ATTRD log item lifecycles.
- Stores logged attr names and values in refcounted shared buffers.
- Formats ATTRI/ATTRD items into log iovecs.
- Creates deferred attr intents and done items.
- Runs deferred attr work through `xfs_attr_set_iter`.
- Relogs attr intents to move the log tail.
- Validates and reconstructs attr intent work during log recovery.
- Cancels completed ATTRIs when ATTRDs are recovered.

## Shared Name/Value Buffers

`struct xfs_attri_log_nameval` stores:
- old name
- new name for parent-pointer replace
- old value
- new value for parent-pointer replace
- refcount

This avoids repeated allocation and copying across rolled transactions and related intent items.

## Supported Operations

- Regular logged xattrs:
  - set
  - remove
  - replace
- Parent-pointer xattrs:
  - set
  - remove
  - replace

Parent-pointer operations require parent support, generation validation, parent namespace flags, and `struct xfs_parent_rec` sized values.

## Recovery Flow

Recovery validates:
- format iovec size
- operation flags
- attr namespace/filter
- name lengths
- value lengths
- parent pointer value contents
- inode number and generation where required
- expected number of log regions

It then reconstructs `xfs_attr_intent`, allocates a transaction with the appropriate reservation, joins the inode, finishes the recovered intent, and captures/commits deferred work.

## Important Invariants

- Each attr deferred operation handles one item at a time.
- ATTRI refcounting accounts for log and ATTRD ownership.
- Regular logged xattr recovery requires logged-xattr filesystem support.
- Parent-pointer recovery uses generation-aware inode lookup.
- `-EAGAIN` from `xfs_attr_set_iter` means the delayed attr state machine needs another transaction roll.

## Dependencies

- XFS deferred operation framework.
- Log item and log recovery infrastructure.
- Attr state machine from `xfs_attr.c`.
- Parent pointer validation.
- Transaction reservation and inode locking code.

## Research Notes

This file is the replayability layer for xattrs. Most subtlety is in validating recovered log vectors before allocation/replay and in preserving shared name/value buffers across relogging.

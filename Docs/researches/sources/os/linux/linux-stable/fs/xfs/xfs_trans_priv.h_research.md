# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_trans_priv.h

## Purpose

Defines private XFS transaction and AIL structures and helper declarations shared by transaction implementation files.

## Main Responsibilities

- Declares private transaction helper functions.
- Defines `struct xfs_ail_cursor`.
- Defines `struct xfs_ail` and AIL state fields.
- Provides inline AIL helpers for minimum item, push, push-all, target reads, and tail assignment.
- Declares AIL cursor, update, insert, delete, and init-facing helpers.
- Provides architecture-aware 64-bit LSN copy helper.

## Important Invariants

- AIL cursor invalidation uses the low bit of the item pointer.
- `ail_lock` protects AIL list, cursor list, target, and tail-update coordination.
- `xfs_trans_ail_update` and related helpers release `ail_lock`.
- 32-bit platforms lock while copying 64-bit LSN values.

## Dependencies

Depends on XFS log item, transaction, AIL, mount, and Linux list/spinlock/waitqueue primitives.

## Research Notes

This header captures the private contract between the transaction core and AIL implementation. The cursor invalidation scheme is the key design detail.

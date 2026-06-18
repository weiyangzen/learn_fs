# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_extfree_item.c

## Purpose

Implements EFI/EFD log intent items for deferred extent freeing. It records extents that must be freed, logs completion records, supports recovery, and handles normal, AGFL, and realtime extent free variants.

## Main Responsibilities

- Manages EFI and EFD slab caches:
  - `xfs_efi_cache`
  - `xfs_efd_cache`
- Implements EFI log item lifecycle:
  - allocation
  - formatting
  - unpin
  - release
  - AIL deletion
  - reference counting
- Implements EFD log item lifecycle:
  - allocation
  - formatting
  - release
  - intent association
- Creates deferred free intents and done items.
- Logs each extent into EFI/EFD formats.
- Sorts free items by group for processing.
- Adds deferred extent-free work through `xfs_extent_free_defer_add`.
- Processes:
  - ordinary data extent frees
  - AGFL block frees
  - realtime extent frees
- Handles transaction roll/retry via copying all EFI extents to the EFD on `-EAGAIN`.
- Validates and recovers EFI items from log recovery.
- Relogs EFI intents to move the log tail forward.
- Registers recovery handlers for EFI/EFD and realtime EFI/EFD log items.

## Important Invariants

- An EFI starts with two references:
  - one for EFI AIL insertion
  - one for EFD completion
- The EFD must be logged after a committed EFI, even if later processing encounters unrelated errors.
- Recovery rejects invalid extents and does not allow mixing realtime and non-realtime extents in a single EFI type.
- AGFL frees bypass normal busy extent insertion and have reserve-specific handling.
- Realtime freeing is only fully enabled under `CONFIG_XFS_RT`.
- Zoned realtime frees call zone allocation code; bitmap-backed realtime frees call rtbitmap code.

## Dependencies

- Uses deferred operation framework through `xfs_defer_op_type`.
- Uses log recovery intent machinery.
- Uses allocator, rmap owner info, AGF buffer, rtbitmap, rtgroup, and zoned allocation helpers.
- Uses `xfs_group_intent_get/put` to pin target AG or rtgroup for deferred items.

## Research Notes

This file is the durable intent layer for freeing extents. Its correctness depends on the EFI/EFD reference model and the ability to recover or cancel every logged free intent exactly once after crashes or transaction rolls.

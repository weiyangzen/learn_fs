# File Research: sources/local-fs/btrfs-linux/fs/btrfs/orphan.h

## Purpose

Declares orphan item insertion and deletion helpers.

## Contents

- Forward declarations for transaction handles and roots.
- Prototypes for `btrfs_insert_orphan_item()` and `btrfs_del_orphan_item()`.

## Role

This is the small public interface for root orphan-item maintenance used by transaction-aware callers.

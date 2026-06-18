# File Research: sources/local-fs/kdave-linux/fs/btrfs/qgroup.h

## Purpose

Defines Btrfs qgroup data structures, mode enums, reservation types, runtime flags, and public quota-group APIs.

## Conceptual Model

The header documents qgroups as three main systems:
- Reserve: pre-charge data/metadata space and enforce limits.
- Trace: record dirty extents whose ownership/reference state may change.
- Account: update qgroup counters, usually during rescan or transaction commit.

It also documents the balance subtree-swap optimization, where swapped subtrees are recorded and only fully traced later if COW modifies a swapped subtree before transaction commit.

## Key Definitions

Runtime-only status flags:
- `BTRFS_QGROUP_RUNTIME_FLAG_CANCEL_RESCAN`
- `BTRFS_QGROUP_RUNTIME_FLAG_NO_ACCOUNTING`

Reservation types:
- `BTRFS_QGROUP_RSV_DATA`
- `BTRFS_QGROUP_RSV_META_PERTRANS`
- `BTRFS_QGROUP_RSV_META_PREALLOC`

Modes:
- disabled
- full
- simple

Main structs:
- `btrfs_qgroup_extent_record`: dirty extent record, including length, optional data reservation to free at commit, refroot, and old roots.
- `btrfs_qgroup_swapped_block`: delayed subtree-swap record used by relocation/balance.
- `btrfs_qgroup_rsv`: per-type reserved byte counters.
- `btrfs_qgroup`: qgroup counters, limits, reservations, relation lists, iterator nodes, rb-tree node, temp ref counts, and sysfs kobject.
- `btrfs_qgroup_list`: parent/member relation glue.
- `btrfs_squota_delta`: simple quota delta event.

## Public APIs

The header exposes:
- mode helpers
- quota enable/disable/rescan/wait/resume
- qgroup relation create/delete
- qgroup create/remove/limit
- dropped subvolume cleanup
- config read/free
- dirty extent trace/account functions
- snapshot inheritance validation/application
- reservation APIs for data and metadata
- swapped-block lifecycle and delayed subtree accounting
- simple quota delta recording
- sanity-test count verification under `CONFIG_BTRFS_FS_RUN_SANITY_TESTS`

## Role in the System

This is the public contract for quota code used across Btrfs transaction, inode, extent, relocation, and ioctl paths.

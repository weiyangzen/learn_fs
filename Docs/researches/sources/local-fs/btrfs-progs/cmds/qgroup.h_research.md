# File Research: sources/local-fs/btrfs-progs/cmds/qgroup.h

## Purpose

Declares qgroup accounting structures and the query helper exported from `qgroup.c`.

## Main Definitions

- `struct btrfs_qgroup_info`
  - `generation`
  - `referenced`
  - `referenced_compressed`
  - `exclusive`
  - `exclusive_compressed`

- `struct btrfs_qgroup_stats`
  - `qgroupid`
  - `info`
  - `limit`

## Exported Function

- `int btrfs_qgroup_query(int fd, u64 qgroupid, struct btrfs_qgroup_stats *stats);`

## Role in the Codebase

Provides a small public interface for consumers that need to query one qgroup’s accounting and limits without using the full `qgroup show` command path.

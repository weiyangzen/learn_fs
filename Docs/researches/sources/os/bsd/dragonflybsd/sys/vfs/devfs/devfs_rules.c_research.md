# File Research: sources/os/bsd/dragonflybsd/sys/vfs/devfs/devfs_rules.c

Read completely: 486 lines.

## Role

This file implements the `/dev/devfs` rule-control device and the in-kernel devfs rule list. Rules can hide, show, create aliases, or change ownership/permissions for devfs nodes, scoped by mount point, jail state, device type, and wildcard name patterns.

## Main Responsibilities

- Define the `devfs` control character device and its open/close/ioctl handlers.
- Allocate, insert, remove, clear, and free rules:
  - `devfs_rule_alloc()`
  - `devfs_rule_free()`
  - `devfs_rule_insert()`
  - `devfs_rule_remove()`
  - `devfs_rule_clear()`
- Apply or reset rules on nodes:
  - `devfs_rule_check_apply()`
  - `devfs_rule_reset_node()`
- Match rule names against node paths with `devfs_rule_checkname()`.
- Create rule-driven aliases with `devfs_rule_create_link()`.
- Handle ioctls:
  - `DEVFS_RULE_ADD`
  - `DEVFS_RULE_APPLY`
  - `DEVFS_RULE_CLEAR`
  - `DEVFS_RULE_RESET`
- Initialize and uninitialize the control device and rule object cache.

## Synchronization and Lifetime Model

- `devfs_rule_lock` serializes the global `devfs_rule_list`.
- `devfs_rule_check_apply()` can be called when the rule lock is already held; otherwise it takes the lock itself.
- Rules own duplicated strings for mount point, optional device name pattern, and optional link name.
- Rule reset can garbage-collect rule-created links and decrement their target node link counts.

## Important Interactions

- Calls into `devfs_core.c` helpers:
  - `devfs_alias_create()`
  - `devfs_gc()`
  - `devfs_resolve_name_path()`
  - `devfs_resolve_or_create_path()`
  - `devfs_WildCaseCmp()`
  - `devfs_apply_rules()`
  - `devfs_reset_rules()`
- Rule filtering uses mount jail state from `DEVFS_MNTDATA(mp)->jailed`.
- Device-type filtering uses `dev_is_good()` and `dev_dflags()`.

## Notable Design Details

- The control device can only be opened read-write and rejects nonblocking open.
- A `* hide` rule intentionally does not hide `/dev/devfs`, so rule management remains possible.
- Name rules resolve optional path prefixes and only match children of the resolved parent directory.
- Link rules support a trailing `*` in the rule name; generated link names append the wildcard suffix from the matching device name.

## Research Notes

- The rule allocator validates required strings only by null/empty checks and duplicates them into kernel memory.
- `devfs_dev_uninit()` notes that rule cleanup is incomplete with a comment: rules should be destroyed before the cache is destroyed.
- Rule application mutates node visibility and permissions directly; vnode/namecache users rely on devfs vnode operations to honor those flags.

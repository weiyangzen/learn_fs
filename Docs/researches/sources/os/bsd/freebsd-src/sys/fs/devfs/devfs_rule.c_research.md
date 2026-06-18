# File Research: sources/os/bsd/freebsd-src/sys/fs/devfs/devfs_rule.c

Read completely: 822 lines.

Purpose: implements devfs rulesets: privileged user-configurable rules that match devfs entries and change visibility, owner, group, mode, or include another ruleset.

Key structures:
- `struct devfs_krule` wraps user ABI `struct devfs_rule` with list linkage and parent ruleset pointer.
- `struct devfs_ruleset` stores ordered kernel rules, ruleset number, and reference count.
- `sx_rules` serializes ruleset/rule mutations and application.

Public entry points:
- `devfs_rules_apply()` applies the active mount ruleset to a newly created dirent.
- `devfs_rules_ioctl()` handles rule/ruleset ioctls after `PRIV_DEVFS_RULE`.
- `devfs_rules_cleanup()` drops a mount’s active ruleset reference.
- `devfs_ruleset_set()` changes a mount’s active ruleset.
- `devfs_ruleset_apply()` reapplies the current ruleset to a mount.

Supported ioctls:
- `DEVFSIO_RADD`, `RDEL`, `RAPPLY`, `RAPPLYID`, `RGETNEXT`.
- `DEVFSIO_SUSE`, `SAPPLY`, `SGETNEXT`.

Matching/action behavior:
- Conditions are ANDed.
- `DRC_DSWFLAGS` matches active cdev driver flags.
- `DRC_PATHPTRN` uses `fnmatch()` against device name, symlink path, or directory path.
- Actions can hide/unhide (`DE_WHITEOUT`), set uid/gid/mode, or include another ruleset recursively up to `devfs_rule_depth`.

Ruleset lifecycle:
- Ruleset 0 is special/null and is not modified.
- Rule number 0 means auto-number; numbering starts at 100 and increments by 100.
- Empty unreferenced rulesets are reaped.
- Include actions increment/decrement referenced ruleset refcounts.

Research notes:
- The file is carefully organized around locking discipline: public functions lock, static helpers assume locks.
- Temporary one-shot rule application is implemented by allocating a transient `devfs_krule`.

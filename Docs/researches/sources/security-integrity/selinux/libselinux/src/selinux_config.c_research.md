<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/selinux_config.c -->
# sources/security-integrity/selinux/libselinux/src/selinux_config.c

## Purpose
Owns libselinux configuration parsing and derived path construction for policy roots, context files, booleans, translations, and related SELinux configuration files.

## Important APIs, Types, And Functions
`selinux_getenforcemode()` reads `SELINUX=`. `selinux_getpolicytype()`, `selinux_set_policy_root()`, `selinux_reset_config()`, `selinux_policy_root()`, and many `selinux_*_path()` accessors expose cached paths. `init_selinux_config()` parses `SELINUXTYPE=` and `REQUIRESEUSERS=`, defaults to `targeted`, and builds `file_paths[]` from `file_path_suffixes.h`.

## Control Flow
Initialization is lazy via `__selinux_once()`. Reset frees all cached strings and reinitializes. `selinux_current_policy_path()` first prefers `<selinux_mnt>/policy`, then searches descending `policy.N` files from the kernel version.

## State And Persistence Behavior
Process-global cached strings hold policy type, policy root, and all derived paths. Disk state is only read from `/etc/selinux/config` and policy-root files.

## Dependencies And Integration Points
This module feeds nearly every policy/config consumer: policy load, media contexts, securetty, seusers, label file paths, and utilities. It uses `require_seusers` from `seusers.c`.

## Risks And Test Signals
Risks include one-time init plus manual reset interactions, partial allocation failure leaving incomplete `file_paths`, global state mutation from `selinux_set_policy_root()`, and permissive parsing. Tests should cover absent config, whitespace/case variations, disabled/enforcing/permissive values, policy-root override, reset after chroot-like changes, and all accessors returning source-tree-consistent paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/selinux_config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/stringrep.c -->
# sources/security-integrity/selinux/libselinux/src/stringrep.c

## Purpose
Converts SELinux class and permission names to numeric values and numeric values back to strings by discovering policy data from selinuxfs.

## Important APIs, Types, And Functions
`discover_class()` reads `<selinux_mnt>/class/<name>/index` and permission files. Public helpers include `string_to_security_class()`, `mode_to_security_class()`, `string_to_av_perm()`, `security_class_to_string()`, `security_av_perm_to_string()`, `security_av_string()`, `print_access_vector()`, and `selinux_flush_class_cache()`.

## Control Flow
Class discovery validates class names, allocates a cache node, reads the numeric class index, scans permissions, and inserts the node into a process-global linked-list cache. Permission lookup maps through `mapping.c`.

## State And Persistence Behavior
State is a process-global class cache populated lazily and freed only by `selinux_flush_class_cache()`. It reads selinuxfs and writes no persistent data.

## Dependencies And Integration Points
Used by compute utilities, mapping setup, AVC helpers, and restore/exec transition code. It depends on `selinux_mnt`, class/perms selinuxfs layout, and mapping helpers.

## Risks And Test Signals
Risks include non-thread-safe cache mutation, stale cache after policy reload, sparse permission arrays stopping early in `string_to_av_perm()`, and mode-to-class coverage. Tests should cover cache flush, unknown classes/perms, policy reload behavior, all file modes, and printing known/unknown permission bits.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/stringrep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/normalize_syscall_map.h -->
# sources/security-integrity/audit-userspace/auparse/normalize_syscall_map.h

## Purpose
Classifies syscall names into internal normalized object/action categories.

## Important APIs, types, and functions
The `_S` table maps syscall strings to `NORM_*` classes for file access/stat/chmod/chown/xattr/mount/rename/delete/time/exec, sockets, process signaling, UID/GID changes, time/system-name/device/memory/scheduler changes, and newer security module syscalls.

## Control flow
Generated `normalize_syscall_map_s2i` is called by `normalize_syscall` after resolving the syscall name. The resulting class drives action phrases, object selection, and attribute collection.

## State and persistence behavior
Static string-to-id table only.

## Dependencies and integration points
Depends on `normalize-internal.h` and libaudit syscall naming. It must stay aligned with `interpret.c` argument decoding and Linux syscall additions.

## Risks and test signals
Risks are missing new syscalls, classifying a syscall into the wrong object model, and arch-specific syscall-name differences. Tests should verify representative syscalls in each class and fallback behavior for unclassified syscalls with audit keys.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/normalize_syscall_map.h -->

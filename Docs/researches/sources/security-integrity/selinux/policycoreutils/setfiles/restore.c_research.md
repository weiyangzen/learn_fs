<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/setfiles/restore.c -->
# sources/security-integrity/selinux/policycoreutils/setfiles/restore.c

## Purpose
Provides shared restorecon initialization, exclusion, glob expansion, and cleanup helpers used by `setfiles`, `restorecon`, `restorecon_xattr`, and noted restorecond integration.

## Important APIs, Types, And Functions
Exports `restore_init()`, `restore_finish()`, `process_glob()`, `add_exclude()`, and global `exclude_list`. It uses `selabel_open`, `selinux_restorecon_set_sehandle`, `selinux_restorecon_set_alt_rootpath`, `selinux_restorecon_set_exclude_list`, `selinux_restorecon_parallel`, and restorecon counters.

## Control Flow
`restore_init()` opens a file-context label handle with validation/path/digest options, assembles `restorecon_flags` from `struct restore_opts`, registers the handle globally with libselinux restorecon, applies an alternate root path, and installs excludes. `process_glob()` expands a user path with tilde/period/nocheck/brace flags, skips trailing `/.` and `/..`, then calls `selinux_restorecon_parallel()` for each result and accumulates skipped-error and relabeled-file counters. `add_exclude()` appends absolute directories to a NULL-terminated list.

## State And Persistence
The helpers own the selabel handle and process-global libselinux restorecon handle/exclusion state. `process_glob()` can relabel filesystem objects depending on flags passed by callers.

## Dependencies And Integration Points
It is the shared adapter between command-line options and libselinux restorecon internals.

## Risks And Edge Cases
`add_exclude()` exits on relative paths. Global `exclude_list` and restorecon handle make concurrent embedding risky unless callers isolate processes. Globbing with `GLOB_NOCHECK` means unmatched patterns are still processed.

## Test Signals
Test exclude list construction/freeing, alternate root errors, digest/validate option propagation, glob patterns including unmatched and brace forms, thread counts, and relabeled/skipped counter accumulation.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/setfiles/restore.c -->

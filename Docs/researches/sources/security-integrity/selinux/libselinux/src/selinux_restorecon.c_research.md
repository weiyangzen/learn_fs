<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/selinux_restorecon.c -->
# sources/security-integrity/selinux/libselinux/src/selinux_restorecon.c

## Purpose
Implements `selinux_restorecon()` and related APIs for computing default file labels from file-context specs, applying xattrs, skipping unchanged subtrees via digests, excluding non-seclabel filesystems, and optionally walking in parallel.

## Important APIs, Types, And Functions
Public APIs include `selinux_restorecon()`, `selinux_restorecon_parallel()`, `selinux_restorecon_set_sehandle()`, `selinux_restorecon_default_handle()`, `selinux_restorecon_set_exclude_list()`, `selinux_restorecon_set_alt_rootpath()`, `selinux_restorecon_xattr()`, and counters for skipped errors and relabeled files. Key internals are `restorecon_sb()`, `selinux_restorecon_common()`, `safe_open()`, `walk_next()`, `selinux_restorecon_thread()`, digest helpers, and inode association helpers.

## Control Flow
Common setup maps flags into `struct rest_flags`, lazy-initializes a default selabel handle, resolves paths, opens the root safely with `O_PATH|O_NOFOLLOW`, and either labels one node or recursively walks a directory tree. Recursive walking uses an explicit directory stack, optional worker threads sharing `rest_state`, cycle checks, mount/exclude pruning, sysfs partial-match pruning, digest skip/write decisions, and per-entry `restorecon_sb()` calls.

## State And Persistence Behavior
Persistent effects are `security.selinux` xattr writes and optional `security.sehash` digest xattr writes/removals. Process-global state includes the file-context handle, exclude list, alt root path, xattr report list, skipped/relabeled counters, and file-spec hash. Thread-shared state is protected by mutexes where needed.

## Dependencies And Integration Points
Integrates with selabel file backend, SHA1 digest code, context manipulation, xattr syscalls, `/proc/self/fd` labeling fallback, `statfs` filesystem filtering, syslog, pthread optional support, and restorecon public flags.

## Risks And Test Signals
Risks include TOCTOU around path traversal, shared-state locking in parallel mode, digest skip correctness, custom-label preservation, conflicting hardlink specs, ignored error accounting, alt-root path slicing, and root/global handle ownership. Tests should cover no-change/verbose/syslog modes, recursive and parallel walks, symlinks, hardlinks, excluded mounts, xdev boundaries, customizable contexts, missing files with ignore flag, read-only filesystems, digest hit/miss/write/delete, and abort/count-error semantics.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/selinux_restorecon.c -->

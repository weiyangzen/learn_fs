<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/setfiles/restorecon_xattr.c -->
# sources/security-integrity/selinux/policycoreutils/setfiles/restorecon_xattr.c

## Purpose
Inspects and optionally deletes `security.sehash` restorecon digest extended attributes for directories under a path.

## Important APIs, Types, And Functions
`main()` parses options and uses shared `add_exclude()`/`restore_finish()`. It uses `selabel_open` with `SELABEL_OPT_DIGEST`, `selabel_digest`, `selinux_restorecon_set_sehandle`, `selinux_restorecon_set_exclude_list`, `realpath`, and `selinux_restorecon_xattr`. It consumes `struct dir_xattr` results with statuses `MATCH`, `NOMATCH`, `DELETED_MATCH`, `DELETED_NOMATCH`, and `ERROR`.

## Control Flow
The program requires SELinux enabled, parses display/delete/recurse/ignore-mount/exclude/specfile options, opens a label handle with digest enabled, optionally prints the calculated specfile SHA1 digest and source specfiles, registers excludes, resolves the target path, calls `selinux_restorecon_xattr()`, prints each returned directory digest state, frees the returned linked list, closes the handle, and frees excludes.

## State And Persistence
With `-d` or `-D`, it removes restorecon digest xattrs. Otherwise it is read-only apart from allocation and label-handle state.

## Dependencies And Integration Points
Works with libselinux restorecon digest support and the same exclude mechanism as `setfiles`. It can target alternate file_contexts via `-f`.

## Risks And Edge Cases
Digest display requires the label backend to provide a digest. `realpath()` rejects nonexistent targets. Delete options can invalidate cached relabel optimization for many directories.

## Test Signals
Test digest display, no-comment mode, recursive and mount-ignore flags, exclude handling, nonmatching digest deletion, all-digest deletion, alternate specfile, SELinux-disabled failure, and memory cleanup under empty result lists.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/setfiles/restorecon_xattr.c -->

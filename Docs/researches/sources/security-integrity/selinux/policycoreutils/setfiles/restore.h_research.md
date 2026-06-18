<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/setfiles/restore.h -->
# sources/security-integrity/selinux/policycoreutils/setfiles/restore.h

## Purpose
Defines the shared restorecon option structure and function prototypes for the setfiles-family utilities.

## Important APIs, Types, And Functions
`struct restore_opts` stores individual SELINUX_RESTORECON flags, computed `restorecon_flags`, `rootpath`, `progname`, `selabel_handle *hnd`, selabel option pointers for validate/path/digest, and a debug flag. It declares `restore_init`, `restore_finish`, `add_exclude`, `process_glob`, and `extern char **exclude_list`.

## Control Flow
Callers initialize a `restore_opts`, set fields from command-line options, call `restore_init()`, call `process_glob()` or other libselinux operations, then call `restore_finish()`.

## State And Persistence
The header itself persists no state, but its structure controls relabel, digest, validation, traversal, audit, and error-count behavior in callers.

## Dependencies And Integration Points
Includes libsepol, libselinux label/restorecon, syslog, fts, stat, and standard system headers. This makes it the ABI-like contract among `setfiles.c`, `restore.c`, and `restorecon_xattr.c`.

## Risks And Edge Cases
Because flags are stored as unsigned ints and ORed later, callers must only assign compatible libselinux flag constants. New libselinux flags require coordinated additions here and in `restore_init()`.

## Test Signals
Compile all consumers after any struct change, and verify each command-line option maps to the expected struct field and final restorecon flag set.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/setfiles/restore.h -->

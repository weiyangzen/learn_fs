# sources/sync-backup/rsync/testsuite/acls-default_test.py

Purpose: verifies that destination parent default POSIX ACLs influence newly created transfer directories and files even when the ACL-bearing parent is outside the transfer itself.

Important APIs/types/functions: `run_rsync('-VV')` gates on ACL support, environment variable `setfacl_nodef` selects default-ACL clearing syntax, helper `testit(dirname, default_acl, file_expected, prog_expected)`, `check_perms`, `test_skipped`, and `test_fail`.

Control flow: seed `SCRATCHDIR` with a default ACL to prove ACL support, create source `dir`, `file`, and executable `program`, change umasks, then call `testit()` for several default ACL and no-default ACL cases. Each case clears inherited defaults, optionally installs a default ACL, runs directory/file transfers into fresh destinations, and checks mode strings for container dirs, regular files, executable files, single-file local-name transfer, and sole-directory transfer.

State and persistence behavior: modifies scratch ACLs, umask, and destination file modes. The important persisted state is the mode inherited through destination default ACLs when rsync creates names.

Dependencies and integration points: depends on rsync ACL support, `setfacl`, the harness-provided `setfacl_nodef`, filesystem ACL support, and `rsyncfns.check_perms`.

Risks and test signals: skips on unsupported ACL tooling. Failures mean rsync ignored default ACL inheritance or incorrectly handled single-file/local-name and directory-only creation paths. Ambient umask is deliberately varied and not incidental.

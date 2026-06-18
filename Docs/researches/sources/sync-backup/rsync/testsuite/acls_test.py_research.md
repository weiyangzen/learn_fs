# sources/sync-backup/rsync/testsuite/acls_test.py

Purpose: shallow POSIX ACL preservation test for `rsync -A`, with support for either GNU `setfacl` or macOS-style `chmod +a` ACL manipulation.

Important APIs/types/functions: `_chmod_plus_a_supported`, `_setfacl`, `_chmod_acl`, `see_acls`, `run_rsync('-avvA')`, `makepath`, and harness skip/fail helpers.

Control flow: gate on rsync ACL support. Create directory `foo` and files `file1`/`file2`, install several user/group ACL entries using the available ACL command surface, run rsync from `FROMDIR` into `TODIR`, capture ACL listings in source and destination cwd, and fail if listings differ.

State and persistence behavior: writes ACL metadata to three source entries and stores the expected ACL listing in `SCRATCHDIR/acls.txt`. The tested persistent state is exact ACL list preservation through archive transfer.

Dependencies and integration points: depends on `rsyncfns` scratch paths, host ACL tooling, `setfacl_nodef`, and platform ACL listing differences.

Risks and test signals: may skip on unsupported platforms or filesystems. Signal is strict source-vs-destination ACL listing equality, so harmless formatting changes in external tools can be noisy.

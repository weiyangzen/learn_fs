# sources/test-tools/pynfs/nfs4.0/servertests/st_rename.py

Purpose: Comprehensive `RENAME` suite covering valid renames for regular and special objects, source/current filehandle non-directory failures, no source filehandle, nonexistent and invalid names, dot names, overwriting directories/files, no-op self renames, hard-link renames, and closing an open target after replacement.

Important APIs/types/functions: Uses `environment.check/get_invalid_utf8strings`, `c.rename_obj`, `c.maketree`, `c.create_obj`, `c.link`, and object constants for symlink/block/char/fifo/socket creation. Public tests include `testValid*`, `testSfh*`, `testCfh*`, `testNoSfh`, `testNonExistent`, name validation tests, overwrite matrix tests, `testSelfRenameDir`, `testSelfRenameFile`, `testLinkRename`, and `testStaleRename`.

Control flow: Positive tests create source and target directories then call `rename_obj(old, new)`. Negative tests deliberately set source or target parent to non-directories or pass invalid old/new components. No-op tests inspect returned source and target change-info values.

State and persistence behavior: Performs filesystem namespace mutations and observes change info before/after values. `testStaleRename` keeps an open stateid across replacement and confirms close still succeeds.

Dependencies and integration points: Depends on server hard-link support for `testLinkRename`, special object creation support, and name validation samples.

Risks: Several checks accept POSIX-vs-RFC alternatives (`EXIST` vs `NOTDIR`/`ISDIR`, `BADNAME` vs `OK`). Disabled/indented legacy extra tests remain at the bottom and are not normal module-level tests.

Test signals: Expected statuses include `NFS4_OK`, `NFS4ERR_NOTDIR`, `NFS4ERR_SYMLINK`, `NFS4ERR_NOFILEHANDLE`, `NFS4ERR_NOENT`, `NFS4ERR_INVAL`, `NFS4ERR_BADNAME`, `NFS4ERR_EXIST`, `NFS4ERR_ISDIR`, and `NFS4ERR_NOTEMPTY`, plus direct failures on unexpected change-info changes.

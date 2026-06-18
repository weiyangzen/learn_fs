# sources/test-tools/pynfs/nfs4.0/servertests/st_remove.py

Purpose: Tests NFSv4 `REMOVE` for all removable object types, non-directory current filehandle errors, missing filehandle, zero-length and invalid UTF-8 target names, nonexistent targets, dot names, and nonempty directory removal.

Important APIs/types/functions: Uses `nfs_ops.NFS4ops.remove`, `environment.check/get_invalid_utf8strings`, and object constants `NF4LNK`, `NF4BLK`, `NF4CHR`, `NF4FIFO`, and `NF4SOCK`. Public tests run from `testDir` through `testNotEmpty`.

Control flow: Positive tests create an object under `c.homedir`, then run `use_obj(parent) + REMOVE(name)`. Negative tests point the current filehandle at non-directories, use invalid names, or build a nonempty directory before removal.

State and persistence behavior: Creates and removes filesystem objects under the test directory; mode and invalid-name tests are otherwise local to temporary paths.

Dependencies and integration points: Depends on create helpers for special objects and fixture paths for existing non-directory current filehandles.

Risks: Invalid UTF-8 coverage is ganesha-flagged. Dot-name behavior permits either `BADNAME` or `NOENT`. Extra indented legacy methods appear after the main tests and look like disabled/unreachable ported test fragments.

Test signals: Checks `NFS4_OK`, `NFS4ERR_NOTDIR`, `NFS4ERR_SYMLINK`, `NFS4ERR_NOFILEHANDLE`, `NFS4ERR_INVAL`, `NFS4ERR_NOENT`, `NFS4ERR_BADNAME`, and `NFS4ERR_NOTEMPTY`.

# sources/test-tools/pynfs/nfs4.0/servertests/st_readdir.py

Purpose: Exercises `READDIR` for empty and populated directories, requested attributes, cookie continuation, non-directory current filehandles, missing filehandles, count limits, dircount behavior, write-only attributes, reserved cookies, and inaccessible directories.

Important APIs/types/functions: Imports `get_attr_name` and `environment.check`. `_compare` validates returned entry names and exact requested attribute sets; `_try_notdir` centralizes non-directory checks. Public tests run from `testEmptyDir` through `testUnaccessibleDirAttrs`.

Control flow: Tests create directory trees with `c.maketree`, call `c.do_readdir` or explicit `c.readdir`, and check returned entries/cookies/errors. Attribute tests compare `e.attrdict` against requested lists.

State and persistence behavior: Creates temporary directory trees and changes mode to `0` for access-denial tests. It observes directory cookies and verifier/count behavior returned by the server.

Dependencies and integration points: Uses environment attribute metadata and client helpers for tree creation, `READDIR` construction, and supported attributes.

Risks: The `testSubsequent` loop decreases `maxcount` until cookie counts split; unusual servers may make this slow or fail to split. Access-denial behavior is credential and export-policy sensitive. Attribute filtering can expose server bugs or unsupported optional attributes.

Test signals: Expects `NFS4_OK`, `NFS4ERR_NOTDIR`, `NFS4ERR_SYMLINK`, `NFS4ERR_NOFILEHANDLE`, `NFS4ERR_TOOSMALL`, `NFS4ERR_INVAL`, `NFS4ERR_BAD_COOKIE`, and `NFS4ERR_ACCESS`; `_compare` calls `t.fail` for entry or attribute mismatches.

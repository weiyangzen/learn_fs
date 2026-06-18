# sources/test-tools/pynfs/nfs4.0/servertests/st_lookup.py

Purpose: Tests NFSv4 `LOOKUP` over the standard pynfs test tree and malformed component cases: existing object types, missing names, zero-length names, long names, non-directory current filehandles, inaccessible directories, dot components, invalid UTF-8, and malformed opaque XDR.

Important APIs/types/functions: Imports `environment.check/get_invalid_utf8strings`, `rpc.rpc`, and `nfs_ops.NFS4ops`. Public tests include `testDir`, `testFile`, `testLink`, `testBlock`, `testChar`, `testSocket`, `testFifo`, `testNoFh`, `testNonExistent`, `testZeroLength`, `testLongName`, `test*NotDir`, `testNonAccessable`, `testInvalidUtf8`, `testDots`, `testUnaccessibleDir`, and `testBadOpaque`.

Control flow: Tests build compound op lists with `c.use_obj`, `c.go_home`, `op.lookup`, `op.putrootfh`, `c.setattr`, and sometimes raw RPC/XDR manipulation. Most cases navigate to a parent filehandle, append one `LOOKUP`, and assert the terminal status.

State and persistence behavior: Creates temporary directories/children and changes mode to `0` for access-denial cases. Otherwise it reads stable fixture paths from `env.opts.usefile`, `usedir`, `uselink`, and device/socket/fifo variants.

Dependencies and integration points: Integrates with the pynfs environment's prebuilt test tree, invalid UTF-8 samples, and `nfs_ops` operation constructors. Raw RPC usage is limited to bad opaque array-length coverage.

Risks: Access tests depend on server permission enforcement and caller credentials. Dot-name behavior allows alternate standards-compatible outcomes (`BADNAME` or `NOENT`). Invalid UTF-8 and malformed XDR paths can vary between strict and permissive servers.

Test signals: Expected statuses include `NFS4_OK`, `NFS4ERR_NOFILEHANDLE`, `NFS4ERR_NOENT`, `NFS4ERR_INVAL`, `NFS4ERR_NAMETOOLONG`, `NFS4ERR_NOTDIR`, `NFS4ERR_SYMLINK`, `NFS4ERR_ACCESS`, `NFS4ERR_BADNAME`, and `NFS4ERR_BADXDR`.

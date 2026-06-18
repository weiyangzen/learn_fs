# sources/test-tools/pynfs/nfs4.0/servertests/st_readlink.py

Purpose: Tests `READLINK` success on symlinks and expected failures on non-symlink object types and missing current filehandle.

Important APIs/types/functions: Uses `nfs_ops.NFS4ops.readlink`, `environment.check`, and fixture paths from `env.opts`.

Control flow: `testReadlink` performs `use_obj(uselink) + READLINK`, extracts `link` from the final result, and compares it to `env.linkdata`. Other tests call `READLINK` against file, block, char, directory, fifo, socket, or no filehandle.

State and persistence behavior: Read-only; no filesystem mutations.

Dependencies and integration points: Depends on a configured symlink fixture with expected `env.linkdata` and standard object fixtures for negative cases.

Risks: Some servers may return alternate errors for special files, but this module expects `NFS4ERR_INVAL` for all non-symlink object types.

Test signals: Success for symlink, `NFS4ERR_INVAL` for non-symlinks, `NFS4ERR_NOFILEHANDLE` when no current filehandle exists, and direct `t.fail` on link-target mismatch.

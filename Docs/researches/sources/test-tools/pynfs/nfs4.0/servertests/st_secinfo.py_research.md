# sources/test-tools/pynfs/nfs4.0/servertests/st_secinfo.py

Purpose: Tests NFSv4 `SECINFO` for an existing file, non-directory current filehandle, nonexistent child, missing filehandle, zero-length and invalid UTF-8 names, and presence of RPCSEC_GSS mechanisms.

Important APIs/types/functions: Uses `nfs_ops.NFS4ops.secinfo`, `environment.check/get_invalid_utf8strings`, and fixture path `env.opts.usefile`. Tests are `testValid`, `testNotDir`, `testVaporFile`, `testNoFh`, `testZeroLenName`, `testInvalidUtf8`, and `testRPCSEC_GSS`.

Control flow: Successful tests navigate to the parent directory and call `SECINFO(filename)`, then inspect the returned mechanism list. Error cases call `SECINFO` with wrong current filehandle or invalid name components.

State and persistence behavior: Creates temporary directories for vapor/invalid-name cases but otherwise reads server security metadata.

Dependencies and integration points: Integrates with server security-flavor configuration. `testRPCSEC_GSS` assumes at least one returned mechanism has flavor `6`.

Risks: Security mechanism availability is export/server-specific; RPCSEC_GSS may not be configured in all test environments. Invalid UTF-8 behavior is ganesha-flagged.

Test signals: Checks success and non-empty mechanism lists, `NFS4ERR_NOTDIR`, `NFS4ERR_NOENT`, `NFS4ERR_NOFILEHANDLE`, and `NFS4ERR_INVAL`; direct failure if RPCSEC_GSS flavor is absent where required.

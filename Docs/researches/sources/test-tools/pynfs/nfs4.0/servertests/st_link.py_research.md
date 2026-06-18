# sources/test-tools/pynfs/nfs4.0/servertests/st_link.py

## Purpose
`st_link.py` tests NFSv4 hard link support and `LINK` operation semantics. It validates advertised link support, linking each object type, source/current filehandle errors, non-directory target directories, duplicate names, invalid names, long names, invalid UTF-8, and dot-name policy.

## Important APIs, Types, And Functions
- `_basictest(t, c, path, error=NFS4_OK)` links `path` into the home directory, checks the expected status, and verifies `FATTR4_NUMLINKS` increases by one when available and successful.
- `testSupported` checks `FATTR4_LINK_SUPPORT` on the home directory.
- `testFile`, `testDir`, `testFifo`, `testLink`, `testBlock`, `testChar`, and `testSocket` cover source object types.
- `testNoSfh`, `testNoCfh`, `testCfh*`, `testExists`, `testZeroLenName`, `testLongName`, `testInvalidUtf8`, and `testDots` cover negative cases.

## Control Flow
The basic flow reads `FATTR4_NUMLINKS`, calls `c.link(source_path, target_path)`, checks the expected status, then re-reads link count for successful cases. No-filehandle tests build raw compounds to omit saved or current filehandles. Invalid UTF-8 tests create a containing directory and iterate shared invalid byte strings from `environment`.

## State And Persistence Behavior
Tests create hard links and directories in the test export, changing link counts and directory contents. Cleanup is delegated to the environment.

## Dependencies And Integration Points
Imports include NFS constants, `check`, invalid UTF-8 generator, and `nfs_ops`. It relies on environment paths and `NFS4Client.link`, `do_getattrdict`, and `create_obj`.

## Risks And Edge Cases
- Some filesystems do not support hard links for special object types; tests use dependency/support metadata to account for this.
- Dot-name behavior accepts OK or BADNAME and can issue warnings, reflecting server policy variance.
- The nested `testNamingPolicy` is not a normal top-level test.

## Test Signals
Signals include `FATTR4_LINK_SUPPORT`, successful link creation and numlinks increment, `NFS4ERR_ISDIR` for directory source, `NFS4ERR_NOFILEHANDLE`, `NFS4ERR_NOTDIR`/`SYMLINK` for invalid current filehandle, `NFS4ERR_EXIST`, `NFS4ERR_INVAL`, `NFS4ERR_NAMETOOLONG`, and invalid UTF-8 rejection.

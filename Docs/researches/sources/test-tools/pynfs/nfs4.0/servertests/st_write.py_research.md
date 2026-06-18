# sources/test-tools/pynfs/nfs4.0/servertests/st_write.py

Purpose: Tests NFSv4 `WRITE` for sync modes, zero and max data, file growth, open stateids, non-file errors, missing filehandle, open-mode/share-deny enforcement, bad/stale/old/stolen stateids, compound writes, large write/read combinations, change attribute granularity, and varied write sizes.

Important APIs/types/functions: Imports XDR types, `check`, `compareTimes`, `makeBadID*`, `makeStaleId`, `struct`, `rpc.rpc`, and `nfs_ops`. `_compare` validates write count/committed/verifier and readback data; `_get_iosize` reads `FATTR4_MAXREAD/MAXWRITE`.

Control flow: Tests create or open files, call `c.write_file` or explicit `op.write`, then often read back data and compare. Large and compound tests build multiple `READ`/`WRITE` ops in one compound. Stateid tests mutate credentials or stateid values.

State and persistence behavior: Writes file data, grows/truncates files, updates change/time metadata, and changes open/share/lock-related server state. `testStolenStateid` temporarily replaces client security credentials.

Dependencies and integration points: Depends on server I/O size attributes, stable write semantics, AUTH_SYS credential behavior, and pynfs XDR packing.

Risks: Large-data tests can be expensive. Some code has Python 3 division/string issues (`maxread/4`, `data = ""` with `struct.pack` bytes) that may be latent in rarely run ganesha tests. Server maxwrite and sync verifier behavior can vary.

Test signals: Checks `NFS4_OK`, `NFS4ERR_ISDIR`, `NFS4ERR_INVAL`, `NFS4ERR_SYMLINK`, `NFS4ERR_NOFILEHANDLE`, `NFS4ERR_OPENMODE`, `NFS4ERR_LOCKED`, `NFS4ERR_BAD_STATEID`, `NFS4ERR_STALE_STATEID`, `NFS4ERR_OLD_STATEID`, `NFS4ERR_ACCESS`, and `NFS4ERR_PERM`, plus byte/count/commit/change-attribute comparisons.

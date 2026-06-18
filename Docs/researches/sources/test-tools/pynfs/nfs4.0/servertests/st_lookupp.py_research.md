# sources/test-tools/pynfs/nfs4.0/servertests/st_lookupp.py

Purpose: Covers NFSv4 `LOOKUPP`, validating parent-filehandle recovery from directories, correct failure for non-directory current filehandles, behavior at root, no-current-filehandle handling, and cross-filesystem parent traversal.

Important APIs/types/functions: Uses `NFS4ops.lookupp/getfh/putrootfh/lookup`, `environment.check`, and fixture paths from `env.opts`. Test functions are `testDir`, `testFile`, `testFifo`, `testLink`, `testBlock`, `testChar`, `testSock`, `testAtRoot`, `testNoFh`, `testXdev`, and `testXdevHome`.

Control flow: Success cases save a filehandle with `GETFH`, descend with `LOOKUP`, call `LOOKUPP`, then compare the restored `GETFH` result. Failure cases build `use_obj(path) + [LOOKUPP]` against non-directories or call `LOOKUPP` without a filehandle.

State and persistence behavior: Creates a temporary child directory for the main parent equality test; otherwise uses static object paths and special cross-device fixture paths.

Dependencies and integration points: Relies on server-test path helpers, special filesystem fixture support for `usespecial`, and compound response array indexing to compare filehandles.

Risks: Symlink handling permits either `NFS4ERR_NOTDIR` or `NFS4ERR_SYMLINK`. Cross-filesystem parent behavior depends on how the export namespace maps mount roots and may be server-specific.

Test signals: Checks `NFS4_OK`, `NFS4ERR_NOTDIR`, `NFS4ERR_SYMLINK`, `NFS4ERR_NOENT`, and `NFS4ERR_NOFILEHANDLE`, plus direct `t.fail` when filehandles differ after parent traversal.

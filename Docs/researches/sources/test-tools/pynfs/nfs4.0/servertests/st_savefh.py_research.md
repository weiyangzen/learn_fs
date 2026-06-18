# sources/test-tools/pynfs/nfs4.0/servertests/st_savefh.py

Purpose: Minimal negative test for `SAVEFH` without a current filehandle; positive save/restore behavior is covered in `st_restorefh.py`.

Important APIs/types/functions: Imports `nfs_ops.NFS4ops.savefh` and `environment.check`; exposes `testNoFh`.

Control flow: Sends a compound containing only `SAVEFH` and expects failure because no current filehandle has been established.

State and persistence behavior: No filesystem persistence; only tests compound-local filehandle preconditions.

Dependencies and integration points: Complements `st_restorefh.py` and shares `savefh` test flags.

Risks: Low; a failure indicates fundamental current-filehandle precondition handling.

Test signals: Expects `NFS4ERR_NOFILEHANDLE`.

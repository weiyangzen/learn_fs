# sources/test-tools/pynfs/nfs4.0/servertests/st_restorefh.py

Purpose: Tests `SAVEFH`/`RESTOREFH` round-tripping for all standard object types and `RESTOREFH` errors when no saved filehandle exists.

Important APIs/types/functions: Uses `nfs_ops.NFS4ops.savefh/restorefh/getfh/putrootfh`, `environment.check`, and helper `_try_sequence`.

Control flow: `_try_sequence` navigates to a path, records `GETFH`, calls `SAVEFH`, switches current filehandle to root, restores saved filehandle, obtains `GETFH` again, and compares both handles. Error tests call `RESTOREFH` without a saved handle, with and without a current root filehandle.

State and persistence behavior: Only compound-local filehandle stack state is mutated; filesystem is read-only.

Dependencies and integration points: Depends on fixture paths for file, directory, fifo, link, block, char, and socket objects.

Risks: Response-array indexing assumes all intermediate operations succeed and remain in a fixed order. Failure message uses saved/restored filehandle comparison as the strongest signal.

Test signals: Success for valid save/restore sequences and `NFS4ERR_RESTOREFH` when there is no saved filehandle.

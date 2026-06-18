# sources/test-tools/pynfs/nfs4.0/servertests/st_putpubfh.py

Purpose: Tests support for `PUTPUBFH` and compares the public filehandle with the root filehandle as an RFC "should" condition.

Important APIs/types/functions: Imports NFS constants, `environment.check`, and `nfs_ops.NFS4ops`. Test functions are `testSupported` and `testSameAsRoot`.

Control flow: `testSupported` sends a single `PUTPUBFH`. `testSameAsRoot` obtains `GETFH` after `PUTPUBFH`, obtains `GETFH` after `PUTROOTFH`, and compares the opaque handles.

State and persistence behavior: Read-only server namespace operation; it only changes the compound current filehandle.

Dependencies and integration points: Uses the server's public filehandle support and root filehandle semantics. Integrated with test flags `putpubfh` and dependency on `PUB1`.

Risks: The spec comparison is advisory, so mismatch calls `t.pass_warn` instead of failing. Some NFSv4 servers may not expose a distinct public handle concept.

Test signals: `check()` validates operation success; mismatched root/public handles produce a warning rather than a failure.

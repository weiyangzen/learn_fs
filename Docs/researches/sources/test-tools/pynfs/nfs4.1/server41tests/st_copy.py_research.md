# sources/test-tools/pynfs/nfs4.1/server41tests/st_copy.py

## Purpose
`st_copy.py` tests server-side `COPY` behavior for the special zero-length copy case, where length zero means copy to EOF.

## Important APIs, Types, and Functions
- `testZeroLengthCopy` creates a source file, writes data, creates a destination file, sends `COPY`, and checks the copied byte count.

## Control Flow
The test opens/creates a source file, writes fixed data, creates a second file, builds a compound of `PUTFH(source)`, `SAVEFH`, `PUTFH(dest)`, and `COPY(source_stateid, dest_stateid, 0, 0, 0, ...)`, then checks that `wr_count` equals the source data length.

## State and Persistence Behavior
It uses open stateids for both source and destination and writes persistent file contents in the test directory for the duration of the test.

## Dependencies and Integration Points
It depends on `create_file`, `write_file`, `nfs_ops.NFS4ops`, and a server implementing `OP_COPY`.

## Risks and Edge Cases
The local `nfs4server.py` read in this group does not implement `op_copy`, so this test is aimed at external servers or later code, not necessarily the embedded test server. It does not explicitly close files after the assertion.

## Test Signals
The core signal is `NFS4_OK` and a `COPY` response count equal to `len(b"write test data")` when copy length is zero.

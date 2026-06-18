# sources/test-tools/pynfs/nfs4.1/server41tests/st_block.py

## Purpose
`st_block.py` contains pNFS block-layout server tests focused on layout stateid sequence handling and `LAYOUTCOMMIT` behavior.

## Important APIs, Types, and Functions
- `testStateid1` validates sequential layout stateid increments across repeated `LAYOUTGET` calls.
- `testStateid2` validates layout merging and commits an updated block extent.
- `testEmptyCommit` sends a normal `LAYOUTCOMMIT` followed by an empty opaque commit.
- `testSplitCommit` sends a disjoint block-layout update with two extents.

## Control Flow
Each test creates a pNFS client session, creates a file, extracts the filehandle and open stateid, sends one or more `LAYOUTGET` operations, unpacks block-layout opaque bodies where needed, builds `pnfs_block_layoutupdate4`, and commits with `LAYOUTCOMMIT`.

## State and Persistence Behavior
The tests exercise server layout state stored behind layout stateids and block extent metadata returned by the filesystem. They expect layout stateid seqids to start at one and increment on later layout grants.

## Dependencies and Integration Points
The module depends on `block.Packer`, `block.Unpacker`, block layout types, `nfs4lib.FancyNFS4Packer`, `get_nfstime`, `create_file`, and the server's pNFS MDS/block support.

## Risks and Edge Cases
The tests are flagged `block` and require a block-layout capable setup. Opaque parsing is noted as not general. Python string/bytes use in empty layoutupdate bodies can be sensitive under Python 3.

## Test Signals
Expected signals are `NFS4_OK` for layoutget and layoutcommit calls, exact layout stateid seqids in `BLOCK1`, and correct acceptance of empty and split layout commit opaque updates.

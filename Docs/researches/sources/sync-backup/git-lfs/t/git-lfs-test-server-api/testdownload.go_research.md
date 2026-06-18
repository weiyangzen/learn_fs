# sources/sync-backup/git-lfs/t/git-lfs-test-server-api/testdownload.go

## Purpose
Download-side compliance tests for the Git LFS batch API probe. It verifies that a server correctly advertises download actions for existing objects and returns object-level 404 errors for missing objects.

## Important APIs, Functions, and Control Flow
`downloadAllExist` calls `callBatchApi` with `tq.Download` for all known-present OIDs, checks that the response count matches input count, and requires each returned transfer to have a `download` relation. `downloadAllMissing` requests only missing OIDs, requires no `download` relation, and requires `o.Error.Code == 404`. `downloadMixed` creates string sets for existing and missing objects, interleaves both classes deterministically, and validates each returned object according to class.

## State, Persistence, and Dependencies
This file does not persist state itself; it reads the `oidsExist` and `oidsMissing` slices provided by `main.go`. It depends on `tq.Transfer.Rel`, `tools.StringSet`, `bytes.Buffer` aggregation, and the shared `callBatchApi` and `interleaveTestData` helpers.

## Integration Points, Risks, and Test Signals
The `init` function registers three tests into the global registry. The main risk is that it validates object class by OID membership rather than order, while still requiring total count. It does not verify response order or actual transfer execution, only batch metadata. Test signals are returned object counts, missing or present download links, and exact 404 object-level error codes.

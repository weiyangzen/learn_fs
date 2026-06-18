# sources/storage-engines/pebble/testdata/make-db.go

## Purpose
This standalone Go program generates deterministic staged Pebble database fixtures for testdata. It accepts a stage number from 1 to 4, opens `db-stage-<stage>` with a fixed format major version, performs mutations up to that stage, and exits with a database representing that lifecycle point.

## Important APIs, Types, and Functions
The file defines `const version = pebble.FormatFlushableIngest`, `usage`, and `main`. It uses `pebble.Open`, `DB.Set`, `DB.Delete`, `DB.Close`, and `pebble.Sync`. Standard library dependencies are `fmt`, `log`, `os`, and `strconv`.

## Control Flow
`main` validates exactly one argument and parses it as an integer in `[1,4]`. Stage 1 opens an empty DB and returns if the requested stage is less than 2. Stage 2 writes `foo=one`, `bar=two`, `baz=three`, overwrites `foo=four`, and deletes `bar`. Stage 3 closes and reopens the DB, which the comments say forces a compaction. Stage 4 writes `foo=five`, writes `quux=six`, and deletes `baz`. A deferred close protects normal exits while setting `db = nil` around the explicit reopen avoids double close.

## State and Persistence Behavior
Each invocation writes a separate Pebble directory named by stage. All mutations use `pebble.Sync`, so fixture creation exercises synced WAL/table state rather than unsynced transient updates. The fixed `FormatMajorVersion` stabilizes on-disk format expectations across generator runs. Reopen at stage 3 persists a lifecycle transition that tests can use to inspect post-open or post-compaction behavior.

## Dependencies and Integration Points
The program is invoked by the adjacent Makefile and depends on the Pebble module itself. It integrates with tests that need small real database directories rather than in-memory DBs. Because it imports the package under test, changes to Pebble format constants, option semantics, or compaction-on-open behavior can affect the generated fixtures.

## Risks and Edge Cases
The generator exits with `log.Fatal` on any Pebble error, so partial fixture directories may remain after failures. It assumes the target directory is already removed by the caller; running it over an existing directory may open and mutate existing state. The "forces a compaction" behavior is implicit rather than asserted by this program. Fixture stability depends on the chosen Pebble format version and any default option changes that influence physical layout.

## Test Signals
Successful execution for stages 1 through 4 is the direct signal. Downstream fixture consumers validate whether the produced database state still matches expected behavior. The printed `Stage N` lines are simple progress diagnostics, not a formal output contract.

# sources/storage-engines/badger/discard_test.go

## Purpose
`discard_test.go` verifies the mmap-backed value-log discard statistics implemented in `discard.go`.

## Important APIs, Types, and Functions
- `TestDiscardStats`: initializes stats, checks empty state, writes 20 counters, iterates expected values, resets the first 10, and verifies reset vs retained values.
- `TestReloadDiscardStats`: opens a DB, updates discard stats, closes, reopens, and checks counters survived.

## Control Flow and State
Both tests create temporary directories and `DefaultOptions`. The first uses `InitDiscardStats` directly; the second reaches discard stats through `db.vlog.discardStats` to validate real DB integration.

## Persistence Behavior
`TestReloadDiscardStats` is the key persistence signal: values written before `db.Close` are expected to be visible after `Open` on the same directory.

## Dependencies and Integration Points
Depends on `os.MkdirTemp`, `testify/require`, `DefaultOptions`, `Open`, `DB.Close`, and `removeDir` from `db_test.go`.

## Risks and Edge Cases
The tests do not force mmap growth beyond the initial 1 MiB file and do not test concurrent `Update` calls. They do cover reset semantics using negative discard values.

## Test Signals
Strong focused coverage for the basic discard-stat lifecycle, but not for large numbers of value-log files, fsync behavior, or race conditions.

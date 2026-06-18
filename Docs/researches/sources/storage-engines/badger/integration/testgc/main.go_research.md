# sources/storage-engines/badger/integration/testgc/main.go

## Purpose
`integration/testgc/main.go` is a standalone long-running integration harness for exercising Badger value-log garbage collection under concurrent writes and reads.

## Important APIs, Types, and Functions
- Globals: `maxValue`, `suffix`.
- `testSuite`: mutex-protected `vals` map plus atomic `count`.
- `encoded`: big-endian uint64 key/value prefix helper.
- `(*testSuite).write`: in one transaction, overwrites random existing keys and appends new never-overwritten keys.
- `(*testSuite).read`: reads a random key, checks value length, and verifies observed versions never go backward for tracked keys.
- `main`: opens DB at `/mnt/drive/badgertest`, starts pprof HTTP server, runs value-log GC goroutine, starts 10 workload goroutines, runs for five minutes, then iterates and validates tracked values.

## Control Flow and State
The workload maintains a monotonic counter. Writes use that counter both as new key source and as value version marker. Reads update an in-memory expectation map guarded by a mutex. A `z.Closer` coordinates shutdown across one GC goroutine and ten worker goroutines.

## Persistence Behavior
The harness deletes and recreates `/mnt/drive/badgertest`, writes real Badger data with `SyncWrites(false)`, runs `RunValueLogGC(0.1)` repeatedly, and finally scans persisted data to check value monotonicity after GC activity.

## Dependencies and Integration Points
Depends on public Badger APIs, `net/http/pprof`, `sync/atomic`, `ristretto/z.Closer`, and Badger `y.AssertTruef`. It is meant for manual/integration execution rather than package unit tests.

## Risks and Edge Cases
The hard-coded `/mnt/drive/badgertest` path and destructive `os.RemoveAll` are hazardous outside a controlled environment. The pprof server listens on localhost:8080 without error handling. The random workload is nondeterministic and uses non-cryptographic `math/rand`.

## Test Signals
Provides high-value manual stress coverage for value-log GC under concurrency. It is not automatically run by `go test` unless invoked as a standalone program.

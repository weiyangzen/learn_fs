## sources/user-network-fs/gcsfuse/internal/gcsx/temp_file_test.go

### Purpose
`temp_file_test.go` unit-tests the public `TempFile` contract from the external `gcsx_test` package, using a wrapper that calls `CheckInvariants` before and after each operation.

### Important APIs, Types, And Functions
Helpers include `readAll`, `dummyReadCloser`, and `checkingTempFile`. `TempFileTest` owns a context, simulated clock, and wrapped temp file. Tests are `Stat_InitialState`, `ReadAt`, `WriteAt`, `Truncate`, and `SetMtime`.

### Control Flow
Setup creates a `NewTempFile` with `initialContent`. Each test drives one operation and then checks stat fields and content. `checkingTempFile` invokes production invariants around read, seek, read-at, write-at, truncate, mtime, stat, and destroy, catching internal dirty-threshold/mtime violations during test execution.

### State, Persistence, And Dependencies
State is a temporary anonymous backing file populated from an in-memory string and a `timeutil.SimulatedClock` fixed to a known time. The test depends on ogletest/oglematchers and the production `gcsx.TempFile` interface.

### Integration Points
The tests provide direct confidence for syncer behavior because `DirtyThreshold`, file size, and mtime are what the syncer consumes. They also validate that the external package can interact with the interface rather than relying on unexported internals.

### Risks
Coverage is focused on short content and happy-path source reading. It does not validate `NewCacheFile`, `RecoverCacheFile`, lazy partial copy behavior, destroy semantics, source I/O errors, or large files. The wrapper assumes invariants should hold around operations but intentionally does not inspect private state.

### Test Signals
Signals verify that initial files are clean, reads do not dirty content, writes dirty from the write offset, truncation dirties at the new size, and explicit mtime sticks until a later modifying method.

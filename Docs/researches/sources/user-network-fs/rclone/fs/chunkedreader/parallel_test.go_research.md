# sources/user-network-fs/rclone/fs/chunkedreader/parallel_test.go

Purpose: tests the parallel chunked reader implementation over multiple mock object seek modes and larger multi-stream scenarios.

Important APIs/functions: `TestParallel` invokes shared `testRead` with three streams. `TestParallelErrorAfterClose` reuses close-error checks. `TestParallelLarge` constructs content larger than multiple chunks and streams, then tests straight reads, rewind, near-start seek, near-end seek, and randomized read/backward-seek loops.

Control flow: `TestParallelLarge` creates one reader for several full-read subtests and a fresh reader for the randomized seek loop. End-relative seeks are converted by passing `offset-size` with `io.SeekEnd`, then `io.ReadAll` verifies the suffix exactly.

State and persistence behavior: no persistence. Tests stress stream state retention, popping, restarting, and seeking within current buffered streams.

Dependencies and integration points: uses `mockobject`, `multipart.BufferSize`, `io`, deterministic random data, and `testify`.

Risks: tests do not force stream open failures, context cancellation, or slow/stalled streams. The first set of subtests shares a reader after full reads and seeks, which validates reuse but can make failures stateful.

Test signals: good behavioral coverage for normal parallel reads and seeks across chunk/stream boundaries.

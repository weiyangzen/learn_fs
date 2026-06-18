# sources/sync-backup/git-lfs/tools/iotools.go

Purpose: I/O helpers for copying with progress, LFS SHA-256 hashing, retriable read wrapping, stream spooling, and NUL-token scanning.

Important APIs/types/functions: `CopyWithCallback`, `NewLfsContentHash`, `HashingReader`, `NewHashingReader`, `NewHashingReaderPreloadHash`, `RetriableReader`, `NewRetriableReader`, `Spool`, and `SplitOnNul`.

Control flow: `CopyWithCallback` first attempts platform clone-file optimization, then falls back to `io.Copy` or a callback reader. `HashingReader.Read` writes successfully read bytes into its hasher. `RetriableReader` preserves nil/EOF/already-retriable errors and wraps other errors. `Spool` buffers 1 KiB in memory, spills the remainder to a temp file, rewinds, and copies combined data to the destination.

State and persistence: `HashingReader` accumulates hash state; `Spool` creates and removes temporary files; callbacks externalize progress state.

Dependencies and integration points: transfer adapters use copy, hashing, and retriable readers for uploads/downloads. Depends on Git LFS `errors`/`tr` and platform `CloneFile`.

Risks: `SplitOnNul` never emits a final unterminated token at EOF. `Spool` returns byte counts from different phases depending on where errors occur. Clone-file optimization bypasses actual byte copy and relies on callback correctness.

Test signals: `iotools_test.go` covers retriable reader behavior; `util_test.go` covers copy callback; transfer tests indirectly exercise hashing/copy paths.

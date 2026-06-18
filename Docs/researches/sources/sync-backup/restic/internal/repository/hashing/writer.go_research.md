## sources/sync-backup/restic/internal/repository/hashing/writer.go

Purpose: `io.Writer` wrapper that forwards writes while hashing the successfully written prefix.

Important APIs/types: `Writer` stores an underlying `io.Writer` and `hash.Hash`. `NewWriter` constructs it. `Write` delegates to the underlying writer, hashes `p[:n]`, panics only if `hash.Hash.Write` violates its no-error contract, and returns the underlying result. `Sum` returns the hash of all successfully written bytes.

Control flow and state: hash state tracks the underlying writer's accepted bytes, which is important for partial writes. No synchronization is provided.

Dependencies and integration points: useful wherever repository code needs streaming content hashes during writes.

Risks and test signals: callers must handle partial write errors according to `io.Writer` semantics; the hash will already include the accepted prefix. Tests cover successful full writes and benchmarks.

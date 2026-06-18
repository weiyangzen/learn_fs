## sources/sync-backup/restic/internal/repository/hashing/reader.go

Purpose: `io.Reader` wrapper that feeds all bytes read into a hash.

Important APIs/types: `Reader` stores an underlying `io.Reader` and `hash.Hash`. `NewReader` constructs it. `Read` delegates to the underlying reader and writes exactly the bytes successfully read into the hash. `Sum` returns the hash sum so far.

Control flow and state: hash state advances monotonically with successful read bytes. Errors from `hash.Hash.Write` are ignored because the interface contract says they are nil.

Dependencies and integration points: used by `checker.go` while streaming pack files to compute the pack content hash without buffering the entire file.

Risks and test signals: callers must use `Sum` after all intended bytes are read. Partial reads with errors still hash the bytes returned, matching Go reader semantics. Tests cover multiple random sizes and benchmarks.

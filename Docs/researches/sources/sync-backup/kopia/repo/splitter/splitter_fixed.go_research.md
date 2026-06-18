# sources/sync-backup/kopia/repo/splitter/splitter_fixed.go

Purpose: implements fixed-size object chunking.

Important APIs/types/functions: `fixedSplitter` stores current offset and chunk length. Methods implement `Close`, `Reset`, `NextSplitPoint`, and `MaxSegmentSize`. `Fixed(length)` returns a splitter factory.

Control flow: `NextSplitPoint` computes remaining bytes until the configured boundary. If the provided slice is shorter, it consumes all bytes and returns `-1`; otherwise it resets offset and returns the boundary length.

State and persistence behavior: in-memory byte count only. The configured length affects persisted object chunk boundaries when used by object writers.

Dependencies/integration: registered under fixed algorithm names and used in tests and repository defaults for older/test configurations.

Risks: zero or negative lengths are not guarded here; callers/factories must provide valid lengths. Deterministic fixed chunking can reduce content-defined dedup effectiveness across shifted data.

Test signals: splitter tests assert exact fixed split counts and segment sizes, including pooled fixed splitters.

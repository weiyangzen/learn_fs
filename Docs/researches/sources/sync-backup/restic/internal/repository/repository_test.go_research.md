
# sources/sync-backup/restic/internal/repository/repository_test.go

Purpose: broad integration and benchmark coverage for the public repository API.

Tests cover saving blobs with supplied or computed IDs, zero-size blob round-trip, flush-time pack merging, save/load benchmarks, variable caller buffer sizes in `LoadBlob`, cache retry on damaged first reads, loading index fixtures, broken unpacked files, retrying transient unpacked corruption, incremental index flushes, invalid compression options, pack handle listing, initialization safeguards, and async blob save callbacks/error handling. Helpers include `damageOnceBackend`, `saveRandomDataBlobs`, and test fixture loading.

State and persistence are realistic: initialized repositories, backend files, cache wrappers, indexes, pack files, config/key files, and async upload goroutines. Integration points span most files in this subset: key/config open, pack manager, pack parser, raw load retry, index flushing, cache clearing, compression, and blob verification. Risks covered include double initialization, corrupted cached data, pack merge counts, duplicate index entries across index files, context cancellation in async saves, and compatibility across repo versions.

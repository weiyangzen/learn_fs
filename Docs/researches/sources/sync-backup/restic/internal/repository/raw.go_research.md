
# sources/sync-backup/restic/internal/repository/raw.go

Purpose: loads raw backend bytes for a repository file without decrypting or parsing, with integrity verification against the file ID for all non-config files.

`Repository.LoadRaw` builds a backend handle, calls `loadRaw`, checks `restic.Hash(buf)` against the requested ID, forgets cached data if present on mismatch, retries once, and returns corrupted bytes with `restic.ErrInvalidData` if the second read still mismatches. Config files are exempt because their ID is the null ID and they bootstrap repository metadata. `loadRaw` reads the full object through `backend.Load` into a `bytes.Buffer`.

State is read-only, except cache invalidation. Integration points include key loading, config backup during upgrades, unpacked file loading, raw repair workflows, and tests that simulate transient corruption. Risks include memory use for full-file loads, relying on hash ID for integrity, and preserving corrupt bytes so repair code can inspect them. Tests validate normal loads, corrupted retry, error wrapping, and cache forget-on-retry.

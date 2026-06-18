
# sources/sync-backup/restic/internal/repository/raw_test.go

Purpose: tests raw backend loading and corruption retry behavior.

`TestLoadRaw` saves random pack files to a memory backend and confirms `LoadRaw` returns exact bytes. `TestLoadRawBroken` uses a mock backend to return corrupted bytes, validates the corrupt data is returned with `restic.ErrInvalidData` after repeated mismatch, then simulates transient corruption fixed on the second read. `TestLoadRawBrokenWithCache` enables cache wrapping and verifies the retry path still succeeds after the first corrupted cached read.

State includes backend objects and optional cache state. Risks covered include missing retry on damaged data, losing diagnostic corrupt bytes, failing to clear cache before retry, and accidentally applying ID checks to config files. These tests are a signal for repository robustness against transient backend/cache corruption.

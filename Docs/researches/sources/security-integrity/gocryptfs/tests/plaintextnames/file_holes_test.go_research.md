# sources/security-integrity/gocryptfs/tests/plaintextnames/file_holes_test.go

## Purpose
Targets sparse-file preservation in `-plaintextnames` mode, where plaintext and ciphertext paths map directly enough to compare hole layouts on both sides.

## Important APIs, Types, And Functions
- `findHolesPretty` wraps `contrib/findholes/holes.Find` and pretty-prints sparse extents.
- `doTestFileHoleCopy` creates a sparse file, copies it repeatedly with `cp --sparse=auto`, verifies MD5s, block usage, and hole/data segment stability.
- `TestFileHoleCopy` defines deterministic and randomized sparse layouts but is currently skipped.

## Control Flow
The helper creates a sparse source, records plaintext and cipherdir hole segments, copies through the mount several times, then compares MD5, disk blocks, and hole maps across copies. Randomized subtests would broaden sparse extent coverage if the skip were removed.

## State And Persistence
It creates multiple plaintext and ciphertext files named from `TestFileHoleCopy.*`. State is local to the plaintextnames test mount and is not cleaned inside the helper beyond initial removal of the base path.

## Dependencies And Integration Points
Depends on GNU `cp --sparse=auto`, `contrib/findholes/holes`, `syscall.Stat`, MD5 helpers, and the plaintextnames package globals `pDir` and `cDir`.

## Risks And Edge Cases
The entire test is skipped with a TODO for recent-kernel failures, so it documents desired behavior more than it protects CI. Sparse detection depends on filesystem allocation heuristics and ext4 extent behavior.

## Test Signals
Current test signal is `SKIP`. If enabled, pass conditions include stable MD5, bounded block-count drift, and identical pretty-printed hole maps across copies.

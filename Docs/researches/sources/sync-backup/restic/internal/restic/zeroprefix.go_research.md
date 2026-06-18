<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/zeroprefix.go -->
# sources/sync-backup/restic/internal/restic/zeroprefix.go

## Purpose
Computes the number of leading zero bits in a byte slice, used by restic ID/search logic that reasons about hash prefixes.

## Important APIs and Control Flow
`ZeroPrefixLen` walks bytes until a non-zero byte, adds eight bits for each zero byte, then uses `bits.LeadingZeros8` for the first non-zero byte. The function exits early on the first non-zero byte and returns all-bit length for an all-zero slice.

## State, Persistence, Dependencies, and Integration
No state is stored. It depends only on `math/bits` and integrates with ID/hash matching logic.

## Risks and Test Signals
Risks are off-by-one bit counts and empty/all-zero handling. Tests cover representative byte patterns, nil/empty behavior, all-zero input, and benchmarks track the hot-path cost.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/zeroprefix.go -->

# sources/object-store/minio-mc/cmd/status.go

## Purpose
Defines a common `Status` interface and two implementations for command progress/accounting: quiet accounting-only status and visible progress-bar status.

## Important APIs, types, and functions
- `Status` combines output, counts, byte progress, lifecycle, message printing, error/fatal helpers, and `io.Reader`.
- `NewQuietStatus` returns `QuietStatus` around an `accounter`.
- `QuietStatus` tracks counts atomically, wraps a hook reader plus accounter, suppresses live progress, and prints final stats.
- `NewProgressStatus` returns `ProgressStatus` around a progress bar.
- `ProgressStatus` tracks counts atomically, wraps a hook reader plus progress bar, renders live progress, and erases progress lines around errors.

## Control flow
Both implementations call `hook.Read(p)` and then read from their accounting/progress reader in `Read`, which lets commands tap the underlying data stream while counting bytes. Counts are updated via 64-bit atomic operations. Quiet status ignores live UI calls and prints messages normally; progress status suppresses per-message printing and updates the progress bar.

## State and persistence
In-memory counts and byte totals only. No persisted state.

## Dependencies and integration points
Uses local `accounter` and `progressBar` types, global `printMsg`, `errorIf`, `fatalIf`, console erase/print helpers, and `probe.Error`.

## Risks and edge cases
- `Read` ignores the return/error from `hook.Read`, which assumes the hook is side-effect-only and non-authoritative.
- `Total()` returns current bytes (`Get`) in both implementations, not the configured total, which may be intentional or surprising.
- Counts are first field in structs to satisfy 64-bit atomic alignment on 32-bit systems.

## Test signals
No direct tests. Tests should cover atomic counts, read accounting, quiet final stats, progress error rendering behavior, and `Total` semantics.

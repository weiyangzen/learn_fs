# sources/sync-backup/rsync/lib/wildmatch.c

## Purpose
`wildmatch.c` implements rsync's shell-style pattern matcher for exclude/include filters and path matching. It supports `?`, `*`, `**`, backslash literals, bracket classes, POSIX character classes, case-insensitive matching, and matching over arrays of path fragments treated as a virtually joined string.

## Important APIs, Types, and Functions
Public functions are `wildmatch()`, `iwildmatch()`, `wildmatch_array()`, and `litmatch_array()`. Internal helpers are `dowild()`, `doliteral()`, and `trailing_N_elements()`. Constants `ABORT_ALL` and `ABORT_TO_STARSTAR` distinguish a hard mismatch from a slash-boundary abort that can still be handled by a `**` wildcard.

## Control Flow
`dowild()` is a recursive matcher that walks pattern and text in tandem. A single `*` does not match slash, while `**` can cross slash boundaries. Character classes handle negation via `!` or `^`, ranges, escapes, and named classes such as `[:alpha:]`. The matcher can consume an array of strings by advancing to the next fragment whenever the current text fragment ends. `wildmatch_array()` optionally restricts matching to trailing path elements or retries the pattern after slash boundaries for "match anywhere below" behavior. `iwildmatch()` toggles the static `force_lower_case` flag around a call to `dowild()`.

## State and Persistence
There is no persistent storage. The static `force_lower_case` flag is process-global and temporarily modified by `iwildmatch()`, which means the matcher is not thread-safe if used concurrently. Optional `wildmatch_iteration_count` state exists under `WILD_TEST_ITERATIONS` for instrumentation.

## Dependencies and Integration Points
The implementation depends on `rsync.h`, ctype-style macros, and rsync's unsigned character typedef. It integrates with filter, include/exclude, daemon module, and file-list logic that need rsync-specific `**` path semantics rather than libc `fnmatch()`.

## Risks
Recursive wildcard matching can be expensive on adversarial patterns with many stars and partial matches. `force_lower_case` only lowercases text, so callers must pass already-normalized patterns for case-insensitive behavior. Slash-special handling is subtle; changing `ABORT_TO_STARSTAR` behavior can break rsync filter semantics. Character-class parsing deliberately aborts malformed classes.

## Test Signals
Tests should cover `*` versus `**`, slash boundaries, `where > 0` trailing element matching, `where < 0` retry-after-slash behavior, arrays split at path separators, bracket negation, escaped characters, POSIX classes, malformed classes, and `iwildmatch()` with uppercase text.

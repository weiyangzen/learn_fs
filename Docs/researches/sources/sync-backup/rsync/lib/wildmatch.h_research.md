# sources/sync-backup/rsync/lib/wildmatch.h

## Purpose
`wildmatch.h` declares the small public interface for rsync's custom wildcard matcher.

## Important APIs, Types, and Functions
The header declares `wildmatch(const char *pattern, const char *text)`, `iwildmatch(const char *pattern, const char *text)`, `wildmatch_array(const char *pattern, const char *const *texts, int where)`, and `litmatch_array(const char *string, const char *const *texts, int where)`.

## Control Flow
There is no control flow in the header. The `where` parameter documented by the implementation determines whole-array matching, trailing path element matching, or slash-boundary retry behavior.

## State and Persistence
The header owns no state. Callers should know that the implementation uses a temporary static case-folding flag for `iwildmatch()`.

## Dependencies and Integration Points
Filter and path-selection code include this header to avoid depending on implementation details. `litmatch_array()` gives callers a cheaper exact-string path matcher with the same virtual-array behavior used by `wildmatch_array()`.

## Risks
The interface exposes only integer truth values and does not report parse errors separately from mismatches. Callers must pass NULL-terminated text arrays to the array functions.

## Test Signals
Compile coverage plus tests that include the header from filter modules are sufficient at the declaration level. Runtime tests belong with `wildmatch.c`.

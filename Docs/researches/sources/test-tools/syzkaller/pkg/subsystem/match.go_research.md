# sources/test-tools/syzkaller/pkg/subsystem/match.go

## Purpose

`match.go` implements path-to-subsystem matching. It compiles `Subsystem.PathRules` into regular-expression matchers and returns all subsystems whose include and exclude rules admit a source path.

## Important APIs, Types, And Functions

`PathMatcher` stores ordered `*match` entries. `MakePathMatcher` constructs a matcher from a subsystem list. `PathMatcher.register` groups rules without excludes into one alternation to reduce matcher count, while preserving rules that need excludes. `PathMatcher.Match` evaluates all matches and deduplicates by `*Subsystem`. `buildMatch` compiles include/exclude regex strings with `regexp.MustCompile`.

## Control Flow, State, Dependencies, And Integration

All state is in-memory and immutable after construction unless callers mutate referenced subsystems. Matching first rejects excluded paths, then requires included paths when an include regexp exists. Results are collected through a map and returned via `slices.Collect(maps.Keys(...))`, so ordering is intentionally unspecified. The matcher is used by `rawExtractor.FromPath`, Linux coincidence building, and subsystem extraction.

## Risks And Test Signals

Regex compilation panics on invalid rules, making list construction fail fast. Empty include with only exclude would match every non-excluded path; current callers should avoid such rules. Result order is nondeterministic, so callers must not rely on it. Tests in `match_test.go` cover deduplication, include/exclude interaction, and rule order independence.

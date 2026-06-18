# sources/sync-backup/syncthing/lib/ignore/ignore.go

## Purpose
Parses `.stignore` files and evaluates Syncthing ignore patterns, including includes, negation, case-folding, deletable flags, skip-dir hints, caching, hashing, and change detection.

## Important APIs, Types, and Functions
`ParseError`, `Pattern`, `ChangeDetector`, `Matcher`, `Option`, `WithCache`, `WithChangeDetector`, `New`, `Load`, `Parse`, `Match`, `Lines`, `Patterns`, `Hash`, `Stop`, `hashPatterns`, `loadParseIncludeFile`, `parseLine`, `parseIgnoreFile`, `WriteIgnores`, and `modtimeChecker`.

## Control Flow
`Load` skips reparsing when remembered files are unchanged, otherwise loads the root ignore file and parses it under lock. Parsing records raw lines, handles `#escape=`, removes duplicate lines, loads `#include` files recursively with loop detection, expands directory-suffix patterns, and compiles gobwas globs. `Match` first ignores Syncthing temp/internal files, checks optional cache, then evaluates patterns in order while tracking whether ignored directories can be skipped.

## State and Persistence Behavior
`Matcher` stores raw lines, compiled patterns, current hash, optional match cache, stop channel, and change detector state. `WriteIgnores` atomically writes ignore contents through `osutil.CreateAtomicFilesystem`, normalizes line endings, closes, and hides the file; empty content removes the ignore file.

## Dependencies and Integration Points
Depends on `fs.Filesystem`, `ignoreresult`, `gobwas/glob`, Unicode normalization, platform build flags, and `osutil`. Used by filesystem watcher filters and scanner ignore logic.

## Risks
Includes can escape the folder root for basic filesystems by design. Cache correctness depends on matcher locking and invalidation when pattern hash changes. Skip-dir inference is subtle around negated/rooted/double-star patterns. Parse errors still leave root `Lines` available.

## Test Signals
This subset includes cache tests; broader ignore parser/matcher tests likely live elsewhere. Key untested edges here include include cycles, custom escape parsing, skip-dir inference, and `WriteIgnores` hiding behavior.

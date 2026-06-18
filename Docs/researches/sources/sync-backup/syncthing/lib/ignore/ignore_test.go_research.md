# sources/sync-backup/syncthing/lib/ignore/ignore_test.go

## Purpose
Exercises the ignore matcher contract: pattern parsing, include expansion, negation, deletable flags, case handling, cache reload behavior, hash stability, line preservation, path-root semantics, skipped-directory decisions, special characters, international wildcards, and escape-directive parsing.

## Important APIs, Types, and Functions
`newTestFS` builds a fake filesystem with `.stignore` and included files. Tests drive `New`, `Load`, `Parse`, `Match`, `Patterns`, `Lines`, `Hash`, `WriteIgnores`, `parseLine`, and `allowsSkippingIgnoredDirs`. `escapeTest`, `backslashTests`, `pipeTests`, and override test tables encode platform-sensitive escaping semantics. Benchmarks cover cached and uncached `Match`.

## Control Flow
Most tests create a fake filesystem, load or parse ignore text, then assert `ignoreresult.R` flags for representative paths. Include tests validate recursive include expansion and missing include errors. Cache tests mutate ignore files and mtimes, reload matchers, and check whether cached match results survive or are invalidated. Escape tests generate pattern variants with `#escape=` before, after, duplicated, invalid, and included lines, then route through `testEscape`.

## State and Persistence Behavior
The tests persist ignore files in the fake filesystem, including file content and modification timestamps, to validate cache keys and reload invalidation. Matcher state inspected includes parsed patterns, original lines, cached match count, and hash values. No production state is written outside fake filesystems.

## Dependencies and Integration Points
Depends on Syncthing `fs`, `osutil`, `rand`, `build`, and `ignoreresult`. The behaviors tested are consumed by scanner and folder code that must know whether paths are ignored, deletable, case-folded, or safe to skip while walking directories.

## Risks
Coverage is broad but primarily table-driven unit behavior; it relies on fake filesystem timestamp manipulation to model cache invalidation. Several paths are platform-gated, so Windows and Darwin behaviors need platform CI. `TestBadPatterns` is skipped, signaling known incomplete validation coverage for malformed glob/include parsing.

## Test Signals
Signals include regression tests for historical issues 3164, 3174, 3639, 3674, 4680, 4689, 4901, and 5009; benchmark coverage for cache performance; and extensive escape directive matrices that protect compatibility across default backslash and pipe escape modes.

# sources/sync-backup/syncthing/lib/fs/casefs.go

## Purpose
Wraps a filesystem to detect case conflicts, making case-insensitive filesystems behave like case-sensitive ones from Syncthing's perspective.

## Important APIs, Types, and Functions
`CaseConflictError`, `IsErrCaseConflict`, `OptionDetectCaseConflicts`, `caseFilesystemRegistry`, `caseFilesystem`, `checkCase`, `checkCaseExisting`, `defaultRealCaser`, `caseCache`, `caseNode`, `newCaseNode`, and `realCase`.

## Control Flow
`NewFilesystem` applies this option as the outermost layer. Mutating and opening operations check input case before delegating; creating/removing/renaming drops cached directory names. `realCase` walks path components through cached directory listings, mapping lowercase-normalized names back to real names. Existing paths whose NFC-normalized real spelling differs from requested spelling return `CaseConflictError`.

## State and Persistence Behavior
Maintains process-local LRU directory-name caches keyed by filesystem type, URI, and options. A background cleaner purges caches every minute. No persistent data is written by the wrapper itself.

## Dependencies and Integration Points
Uses `hashicorp/golang-lru/v2`, Unicode normalization from `x/text`, `UnicodeLowercaseNormalized`, and all wrapped `Filesystem` methods. It is deliberately outside `mtimeFS` and `walkFilesystem`.

## Risks
Cache freshness is central; stale cache triggers retry on not-exist, but other races can still report transient conflicts. `newCaseNode` compares `lower != lastLower` but assigns `lastLower = n`, which may reduce duplicate-fold handling accuracy if adjacent names fold together. Performance depends on directory size and cache invalidation frequency.

## Test Signals
`casefs_test.go` covers real-case lookup, sensitive/insensitive Stat behavior, stress concurrency, and benchmarks. `filesystem_test.go` guards mtime wrapper preservation with case cache reuse.

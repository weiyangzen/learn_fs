# sources/user-network-fs/rclone/backend/googlephotos/pattern_test.go

## Purpose
This file unit-tests Google Photos virtual path matching and entry generation without calling the live API.

## Important APIs, Types, And Control Flow
`testLister` implements the pattern `lister` interface using in-memory album, name, and upload trees. `TestPatternMatch` checks root-relative and nested path matching for directories and files. `TestPatternMatchToEntries` invokes selected `toEntries` callbacks and inspects the first returned remotes. `TestPatternYears`, `TestPatternMonths`, and `TestPatternDays` verify date directory generation. `TestPatternYearMonthDayFilter` checks valid and invalid date filter construction. `TestPatternAlbumsToEntries` verifies album-prefix directory behavior and combined directory plus file listing.

## State And Persistence
All test state is in memory: synthetic albums, mock objects, and a `dirtree.DirTree` for uploaded entries. No network or disk state is used.

## Dependencies And Integration Points
The tests use `api`, `fs`, `dirtree`, `fstest`, `mockobject`, and testify. They are direct guards for `pattern.go` and indirectly protect `googlephotos.go` methods that depend on pattern capabilities.

## Risks And Test Signals
The tests are strong for route selection and expected virtual remotes, but they deliberately sample only the first few generated entries in long year/month/day outputs. They do not verify live API filter results or all regex branches exhaustively.

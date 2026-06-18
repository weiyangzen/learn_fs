# sources/user-network-fs/rclone/backend/googlephotos/pattern.go

## Purpose
This file defines the Google Photos backend's virtual filesystem layout. It maps path strings to regex-backed directory patterns and converts matched paths into directory entries or search filters.

## Important APIs, Types, And Control Flow
`lister` is the subset of `Fs` used by pattern logic. `dirPattern` records a regex, upload/mkdir/file/upload-directory capabilities, and an optional `toEntries` callback. `patterns` defines the tree: root directories `media`, `album`, `shared-album`, `upload`, and `feature`; upload staging paths; all media; year/month/day date views; album/shared-album pseudo-directories; and `feature/favorites`.

`mustCompile` compiles regexes at init. `dirPatterns.match` joins root and item path, derives a prefix relative to root, filters by file-vs-directory pattern, and returns regex captures plus matching pattern. `years`, `months`, and `days` synthesize date hierarchy directories. `yearMonthDayFilter` validates and builds `api.SearchFilter` date filters. `featureFilter` builds a hardcoded FAVORITES filter. `albumsToEntries` combines synthetic album-prefix directories with actual album media listing and returns `fs.ErrorDirNotFound` when a non-root album path matches neither.

## State And Persistence
The file has no mutable persistent state beyond the package-level compiled `patterns` slice. It derives entries from the provided lister, album cache, and upload dirtree.

## Dependencies And Integration Points
It depends on the Google Photos API types, rclone `fs`, package album helpers, and Go regexp/time/path utilities. `googlephotos.go` calls `patterns.match` for `NewFs`, `List`, `Mkdir`, `Rmdir`, `Update`, `Remove`, and metadata lookup.

## Risks And Test Signals
Risks include regex ordering, ambiguous album/file paths, prefix calculation when the remote root is nested, date validation accepting impossible dates like February 31 because only numeric bounds are checked, and stale album/upload data. Unit tests cover matching, generated entries, date hierarchies, date filter validation, and album entry synthesis.

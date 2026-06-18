# sources/user-network-fs/rclone/backend/cache/cache_unsupported.go

## Purpose
This stub prevents Go from reporting "no buildable Go source files" for the cache package on unsupported platforms.

## Important APIs, Types, And Control Flow
The file contains only the package declaration for `cache` and no runtime symbols. Its build constraint is `plan9 || js`, complementing the cache implementation files that use `!plan9 && !js`.

## State And Persistence
There is no state, persistence, initialization, or side effect.

## Dependencies And Integration Points
It integrates only with Go build selection. On unsupported platforms, importing `backend/cache` yields an empty package rather than the full backend implementation.

## Risks And Test Signals
Risk is accidental addition of API surface here, which could mask unsupported behavior. Test signal is compile-only: packages importing `cache` should build on Plan 9 or JS only if they do not require implementation symbols.

# sources/sync-backup/syncthing/lib/model/debug.go

## Purpose
Defines the package logger adapter used by model code.

## Important APIs, Types, and Functions
Declares package variable `l = slogutil.NewAdapter("The root hub")`.

## Control Flow
No runtime control flow beyond package initialization.

## State and Persistence Behavior
Holds a package-global logging adapter. No persistence or domain state.

## Dependencies and Integration Points
Depends on `internal/slogutil`. Older model code and tests use `l.Debugf`, `l.Debugln`, and related adapter methods alongside newer structured `slog` loggers.

## Risks
Global logger naming is broad and shared across the package, so log attribution relies on surrounding fields or messages. It is not test-isolated.

## Test Signals
No direct tests; usage is indirectly compiled throughout the model package.

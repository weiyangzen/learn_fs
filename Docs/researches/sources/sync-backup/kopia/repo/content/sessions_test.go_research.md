# sources/sync-backup/kopia/repo/content/sessions_test.go

## Purpose
Validates session ID creation, session blob parsing, optional clock-skew enforcement, and write-session marker persistence behavior.

## Important APIs, Types, And Functions
Tests include `TestGenerateSessionID`, `TestSessionIDFromBlobID`, `TestCheckClockSkewBounds_Positive`, `TestCheckClockSkewBounds_Negative`, `TestMaybeCheckClockSkewBounds_Disabled`, `TestMaybeCheckClockSkewBounds_Enabled`, `TestWriteSessionMarkerLockedWithoutClockSkew`, and `TestWriteSessionMarkerLockedWithClockSkew`.

## Control Flow
The tests generate multiple IDs at the same time and ensure uniqueness; table-drive blob ID parsing cases; compare local and modification times at and over the skew threshold; and build test write managers over map storage with controlled fake clocks. Marker-write tests enable `KOPIA_ENABLE_CLOCK_SKEW_CHECK` and assert success when manager and storage times match, failure when storage time is just beyond the permitted skew.

## State And Persistence
The marker-write tests persist encrypted marker blobs into `blobtesting.MapStorage`. Fake clock instances provide deterministic local and storage modification times.

## Dependencies And Integration Points
The tests use `blobtesting`, `faketime`, `epoch.DefaultParameters`, `format.ContentFormat`, `index.Version2`, and `NewManagerForTesting`. They exercise the session code through the same `WriteManager` path used by production writers.

## Risks And Edge Cases
The tests explicitly cover unset/false environment variables disabling skew checks, set/true variables enabling them, and boundary behavior at exactly `maxClockSkew`. They do not cover malformed encrypted session marker payloads or duplicate marker resolution in `ListActiveSessions`.

## Test Signals
Coverage is good for clock-skew gating and session naming. Active-session listing is only indirectly covered by constructing marker writes, not by scanning multiple stored marker blobs.

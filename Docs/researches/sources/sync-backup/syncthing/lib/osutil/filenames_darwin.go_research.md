## sources/sync-backup/syncthing/lib/osutil/filenames_darwin.go

Purpose: Darwin filename normalization helpers.

Important APIs: `NormalizedFilename` returns NFC form for Syncthing wire/internal normalized names; `NativeFilename` returns NFD form expected by macOS filesystems.

Control flow and state: stateless calls to `golang.org/x/text/unicode/norm`.

Dependencies and integration points: used where Syncthing converts between native filesystem names and normalized protocol names, including encrypted trailer metadata in model puller state.

Risks: Unicode normalization mistakes can cause duplicate or inaccessible names across platforms.

Test signals: no direct tests in this subset.

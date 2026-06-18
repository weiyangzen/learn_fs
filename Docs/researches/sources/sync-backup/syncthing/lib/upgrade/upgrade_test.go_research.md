# sources/sync-backup/syncthing/lib/upgrade/upgrade_test.go

Purpose: regression tests for version comparison and release selection.

Important tests: `TestCompareVersions` covers equal, older/newer, major transitions, 0.x/1.x special handling, numeric prerelease ordering, string prerelease ordering, build metadata ignoring, and `v`/`V` prefixes. `TestErrorRelease` expects selection failure on nil releases. `TestSelectedRelease` constructs candidate releases with matching assets and checks prerelease filtering, newest minor selection, and major-upgrade deferral behavior. `TestSelectedReleaseMacOS` validates both `macos` and legacy `macosx` asset prefixes on Darwin.

State and persistence: no persistence.

Dependencies and integration: depends on runtime/build OS info for platform-specific asset names.

Risks and signals: strong for selection policy. It does not test HTTP fetching, archive extraction, signature verification, or binary replacement.

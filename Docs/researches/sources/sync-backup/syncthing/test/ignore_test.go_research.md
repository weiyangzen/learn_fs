# Research: sources/sync-backup/syncthing/test/ignore_test.go

## sources/sync-backup/syncthing/test/ignore_test.go

Purpose: integration test for `.stignore` pattern changes and scanner model counts.

Important APIs/functions: `TestIgnores`, `p.Rescan`, and `p.Model`.

Control flow: starts h1, creates directories and files under `s1`, scans and checks all files are visible, writes ignore patterns covering selected names and a case-insensitive txt rule, rescans and checks reduced file count, waits over one second for mtime granularity, writes a less restrictive ignore file, rescans, and checks file count increases.

State and persistence: writes files/directories and `.stignore` under `s1`; updates h1 index.

Dependencies and integration: ignore parser, scanner, model REST API. Risks include case-sensitivity differences, mtime granularity, and count expectations tied to fixture names. Test signal is `Model.LocalFiles` count after each rescan.

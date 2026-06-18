# Research: sources/sync-backup/syncthing/meta/copyright_test.go

## sources/sync-backup/syncthing/meta/copyright_test.go

Purpose: CI/meta test ensuring source files carry acceptable copyright or generated-code headers.

Important APIs/functions: `TestCheckCopyright` walks `copyrightCheckDirs`; `checkCopyright` filters regular `.go` and `.sql` files and scans the top five lines for `copyrightRe`.

Control flow: each configured directory is recursively walked. Files outside the extension set are ignored. Matching any configured regexp allows the file; otherwise `checkCopyright` returns an error naming the path.

State and persistence: read-only scan of repository files. No state is written.

Dependencies and integration: uses `filepath.Walk`, regexps, and OS file reads. It integrates with test/CI policy across `cmd`, `internal`, `lib`, `test`, and `script`. Risks include false negatives for generated files whose header changes, and false positives from broad `Copyright` matching. Test signal is direct via `go test ./meta`.

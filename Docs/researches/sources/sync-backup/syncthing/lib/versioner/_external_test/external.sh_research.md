# sources/sync-backup/syncthing/lib/versioner/_external_test/external.sh

Purpose: helper script for external versioner tests.

Important APIs and control flow: shell script prints both arguments with markers, then removes the target file with `rm -f "$1/$2"`, where `$1` is folder path and `$2` is file path supplied by placeholder expansion.

State and persistence: deletes the test file in the testdata tree.

Dependencies and integration: invoked by `external_test.go` on non-Windows platforms as the configured external versioning command.

Risks and signals: intentionally simple; path quoting is important and covered by test paths with spaces/parentheses.

# Research: sources/sync-backup/syncthing/meta/forbidden_words_test.go

## sources/sync-backup/syncthing/meta/forbidden_words_test.go

Purpose: enforces repository-wide source hygiene by rejecting banned text in Go files.

Important APIs/functions: `TestForbiddenWords` defines checked directories and `forbiddenWords`, currently rejecting the deprecated `"io/ioutil"` import.

Control flow: recursively walks `../cmd`, `../lib`, `../test`, and `../script`; skips `.git`, non-Go files, and generated `.pb.go` files; reads each file and reports any forbidden byte sequence with `t.Errorf`.

State and persistence: read-only repository scan.

Dependencies and integration: uses `bytes.Contains`, `os.ReadFile`, and `filepath.Walk`. It is a CI policy gate. Risks include string-literal false positives and missing generated files by design. Test signal is the failing path and forbidden token.

# sources/sync-backup/restic/cmd/restic/cmd_ls_test.go

Purpose: unit tests for `ls` JSON node encoding and ncdu export formatting.

Important APIs/types/functions: `lsTestNode`; `lsTestNodes`; `TestLsNodeJSON`; `TestLsNcduNode`; `TestLsNcdu`.

Control flow and state: tests build synthetic `data.Node` values for regular files, empty files, symlinks, directories, and sticky/setuid/setgid modes. They assert exact JSON strings for restic JSON-lines nodes and exact ncdu node JSON, then build a small ncdu tree with `ncduLsPrinter`.

Dependencies and integration points: depends on `data.Node` fields, Go `os.FileMode`, JSON encoding, and restic test assertions.

Risks: exact JSON strings intentionally lock the wire format and will fail on field order or naming changes. Zero time and mode behavior is part of the contract.

Test signals: strong serialization regression coverage, including empty-file size emission and non-regular size omission.

# sources/sync-backup/git-lfs/lfs/scanner_test.go

Purpose: Tests log-diff pointer scanning for additions and deletions, including path filtering and quoted/octal path decoding.

Important APIs/types/functions: Exercises `newLogScanner`, `LogDiffAdditions`, `LogDiffDeletions`, `scanner.Scan`, `scanner.Pointer`, `filepathfilter.New`, and helper assertions.

Control flow: A synthetic Git log diff containing deleted, modified, and added pointer documents is scanned in addition or deletion mode. Each test advances the scanner and asserts pointer name, OID, size, and filtering behavior.

State and persistence behavior: All input is an in-memory multiline string. Scanner state tracks the current diff file, plus/minus side, decoded pointer lines, and the latest parsed pointer.

Dependencies and integration points: Validates integration between log parsing, pointer decoding, Git path quoting/unquoting, and `filepathfilter` include/exclude semantics.

Risks and edge cases: Important cases include non-ASCII paths represented by Git octal escapes, pointers with extensions, modifications where both sides are pointers, and filters that include or exclude only matching paths.

Test signals: Good unit coverage for diff parser modes. It does not cover malformed diff input or asynchronous scanner wrappers.

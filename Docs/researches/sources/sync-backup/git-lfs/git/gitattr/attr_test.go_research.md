# sources/sync-backup/git-lfs/git/gitattr/attr_test.go

Purpose: unit tests for `.gitattributes` line parsing in `attr.go`.

Important APIs/types/functions: exercises `ParseLines`, `PatternLine`, `MacroLine`, and `Attr` values. Uses `strings.NewReader` and `testify/assert`.

Control flow: each test parses a small attribute snippet and asserts line count, concrete interface type, pattern/macro text, and ordered attributes. Negative cases assert comments are skipped and unbalanced quotes return the expected error.

State/persistence behavior: in-memory only. No filesystem or Git repository state is required.

Dependencies/integration: provides coverage for downstream consumers that assume parsed attributes preserve left-to-right order and distinguish false from unspecified state.

Risks/test signals: good coverage of common syntax, but does not cover mixed whitespace beyond spaces, line-ending detection, escaped quotes beyond `strconv.Unquote`, or malformed key/value combinations.

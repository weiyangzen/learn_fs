# sources/sync-backup/git-lfs/lfs/pointer_test.go

Purpose: Exercises Git LFS pointer encoding/decoding, canonical-format detection, extension ordering, empty-file handling, and invalid-pointer rejection.

Important APIs/types/functions: Tests cover `NewPointer`, `NewPointerExtension`, `EncodePointer`, `DecodePointer`, `DecodeFrom`, pointer fields `Version`, `Oid`, `OidType`, `Size`, `Extensions`, and `Canonical`, plus `errors.IsNotAPointerError`.

Control flow: Tests construct literal pointer documents, decode from `bytes.Buffer` or `strings.Reader`, and assert parsed fields. Canonical tests run valid and non-canonical examples through the same decoder. Invalid tests iterate malformed samples and require an error.

State and persistence behavior: No persistent state; all data is in-memory buffers. `DecodeFrom` also returns a replay buffer for empty content and computes the empty SHA-256 and size.

Dependencies and integration points: Integrates with the pointer parser/encoder implementation in the `lfs` package and the shared error classification package. Uses `bufio.Reader` to verify line-by-line encoder output.

Risks and edge cases: Covers missing trailing newline, CRLF line endings, trailing whitespace, bad version strings, bad OID type/value, missing fields, extra keys, out-of-order keys, duplicate extension priorities, invalid extension names, and priorities outside supported range.

Test signals: Strong unit coverage for pointer format compatibility, including legacy prerelease version acceptance and extension sorting. It does not cover large-pointer-size performance or streaming decode beyond small literals.

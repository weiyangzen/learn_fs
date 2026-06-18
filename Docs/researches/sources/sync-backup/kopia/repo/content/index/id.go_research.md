# sources/sync-backup/kopia/repo/content/index/id.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/index/id.go_research.md`.

Purpose: defines content IDs and prefixes for content-addressable storage. IDs are optional one-character metadata prefixes plus a variable-length hash up to `hashing.MaxHashSize`.

Important APIs and types: `IDPrefix.ValidateSingle` accepts empty or one character in `g` through `z`. `ID` stores fixed hash bytes, prefix byte, and hash length. Methods cover JSON marshal/unmarshal, `Hash`, `AppendToJSON`, `Append`, `String`, `Prefix`, `HasPrefix`, and internal ordering through `less` and `comparePrefix`. Constructors are `IDFromHash` and `ParseID`; `EmptyID` is the zero ID.

Control flow and semantics: `ParseID` treats odd-length strings as prefixed and even-length strings as raw hex. Prefix validation rejects odd strings with prefixes outside `g` to `z`. `less` sorts unprefixed hex IDs before prefixed IDs and then compares raw hash bytes. `comparePrefix` optimizes empty prefix comparisons and falls back to string comparison otherwise.

State and persistence behavior: IDs are value objects serialized to JSON and encoded in pack indexes. The binary index encoding uses a prefix byte even for unprefixed IDs.

Dependencies: `encoding/hex`, `encoding/json`, `strings`, `bytes`, errors, and hashing constants.

Risks and tests: prefix/ordering rules are fundamental to range scans and pack index binary search. Tests validate valid ordering, JSON round trips, hash construction, invalid parses, prefix validation, `Hash`, `Append`, and `HasPrefix` behavior.

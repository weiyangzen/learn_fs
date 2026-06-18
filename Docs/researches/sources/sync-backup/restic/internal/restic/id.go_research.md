
# sources/sync-backup/restic/internal/restic/id.go

Purpose: defines restic content IDs as SHA-256 hashes and provides parsing, formatting, equality, JSON, and conversion helpers.

Important APIs include `Hash`, `ParseID`, `ID.String`, `(*ID).Str`, `ID.IsNull`, `ID.Equal`, `ID.MarshalJSON`, `(*ID).UnmarshalJSON`, and `IDFromHash`. IDs are fixed 32-byte arrays. `String` always emits full lowercase hex; `Str` emits an 8-character prefix and handles nil/null specially. JSON encoding uses full hex strings; unmarshal requires quotes and exact encoded length.

State is value-only but IDs are the naming and integrity backbone for packs, indexes, keys, snapshots, and blobs. Integration points include backend handles, hash verification, set/map keys, prefix lookup, and tests. Risks include accepting malformed or truncated IDs, accidentally using prefix strings as canonical names, and hash mismatch handling. Tests cover known hashes, equality, JSON round-trip, malformed JSON, null/nil `Str`, and `IDFromHash` expectations elsewhere.

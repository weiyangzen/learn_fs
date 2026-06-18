# sources/sync-backup/kopia/repo/content/index/info.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/index/info.go_research.md`.

Purpose: defines the persisted metadata record for one content entry in a pack index.

Important API: `Info` contains `PackBlobID`, `TimestampSeconds`, original and packed lengths, pack offset, compression header, `ContentID`, deletion flag, content format version, and encryption key ID. `Timestamp` converts `TimestampSeconds` to a `time.Time`.

Control flow, State and persistence: this is a plain value type used in builders, indexes, content manager overlays, recovery, iteration, and JSON/log output. Its timestamp and deleted fields are used by merge and replacement logic to determine the winning entry for duplicate content IDs.

Persistence behavior: fields map directly to index v1/v2 binary formats, though v1 cannot preserve all fields. In v1, compression and encryption key IDs must be zero and original length is reconstructed from packed length and encryptor overhead.

Dependencies: `blob.ID`, compression header IDs, and `time`.

Risks and tests: changes to this struct affect binary index compatibility, content cache keys, deletion semantics, and maintenance behavior. Tests throughout `content_manager_test.go`, `packindex_test.go`, and `merged_test.go` assert expected field preservation and merge precedence.

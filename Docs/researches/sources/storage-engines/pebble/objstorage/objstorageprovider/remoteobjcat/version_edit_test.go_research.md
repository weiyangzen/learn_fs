# sources/storage-engines/pebble/objstorage/objstorageprovider/remoteobjcat/version_edit_test.go

Purpose: This file verifies that `VersionEdit` serialization is stable for representative catalog edits.

Important tests: `TestVersionEditRoundTrip` enumerates empty edits, creator-ID-only edits, single table/blob additions, deletions, and mixed edits containing creator ID, multiple objects, locators, custom object names, cleanup methods, and deleted file numbers. `checkRoundTrip` encodes to a `bytes.Buffer`, decodes into a fresh `VersionEdit`, and compares with `pretty.Diff`.

Control flow and state: The tests are pure round-trip checks. They do not call `VersionEdit.Apply` or `Catalog.ApplyBatch`; the focus is whether an encoded byte stream reconstructs exactly the same struct fields.

Dependencies and integration: The cases use `base.FileTypeTable`, `base.FileTypeBlob`, `objstorage.SharedNoCleanup`, `objstorage.SharedRefTracking`, and `remote.MakeLocator`. This ties the test vectors to the file types and cleanup modes supported by the catalog.

Risks and test signals: It catches missing fields in encode/decode and accidental object-type mapping changes. It does not test corrupt input, unknown tags, duplicate object application, or catalog rotation; those are covered elsewhere or guarded by code assertions.

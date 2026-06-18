# sources/storage-engines/pebble/objstorage/objstorageprovider/remoteobjcat/version_edit.go

Purpose: This file defines the on-disk record format for remote object catalog edits. A `VersionEdit` can add remote objects, delete objects, and set the immutable creator ID.

Important types and functions: `VersionEdit` contains `NewObjects`, `DeletedObjects`, and `CreatorID`. `Encode` writes varint-tagged records. `Decode` reads them, including optional per-new-object tags for locator and custom object name. `Apply` mutates a creator ID pointer and object map. Helper mappings convert between catalog object type codes and Pebble `base.FileType` values.

Control flow: Each new object record encodes file number, object type, creator ID, creator file number, cleanup method, optional locator/custom-name tags, and a zero terminator. Deleted-object and creator-ID records follow their own tags. Decode loops until EOF; unexpected EOF within a known tag becomes `errCorruptCatalog`, while unknown tags are hard errors. Apply sets creator ID first, then adds new objects and deletes removed objects, with invariant assertions for duplicate additions or missing deletions.

State and persistence: This is pure serialization logic, but it is the catalog's compatibility contract. It supports table and blob object types only. Locator redaction is preserved by reconstructing `remote.Locator` from a redactable string.

Dependencies and integration: `catalog.go` writes and reads these records through Pebble's `record` package. The provider's remote catalog metadata maps directly to `RemoteObjectMetadata`.

Risks and test signals: Unknown optional object tags currently fail instead of being skipped, so format extension must be deliberate. Tests round-trip varied edits with creator IDs, tables, blobs, locators, custom names, ref-tracking/no-cleanup methods, and deletions.

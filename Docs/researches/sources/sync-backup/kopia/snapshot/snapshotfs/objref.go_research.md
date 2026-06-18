# sources/sync-backup/kopia/snapshot/snapshotfs/objref.go

Purpose: resolves user-facing snapshot or object references into repository-backed filesystem entries or nested object IDs.

Important APIs/types/functions: `ParseObjectIDWithPath`, `GetNestedEntry`, `FindSnapshotByRootObjectIDOrManifestID`, `FilesystemEntryFromIDWithPath`, `FilesystemDirectoryFromIDWithPath`, `consistentSnapshotMetadata`, and `GetEntryFromPlaceholder`.

Control flow: references may be manifest IDs, root object IDs, or object IDs followed by slash paths. Manifest IDs are tried first; otherwise snapshots sharing the root object are listed and checked for consistent root metadata. Nested paths descend through `fs.Directory.Child`.

State and persistence: read-only; it opens repository objects and manifests but does not write.

Dependencies and integration points: supports CLI restore/browse paths, shallow placeholder expansion, and object ID parsing via `repo/object` and `repo/manifest`.

Risks and test signals: multiple snapshots can share root objects but differ in root attributes; `consistentAttributes` decides whether that is an error or latest-manifest selection. Nested paths disable consistency checks because parent entries carry attributes.

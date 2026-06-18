# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/helpers/OmFSOFile.java

Purpose: `OmFSOFile` is a helper value object for file-system-optimized buckets. It precomputes volume ID, bucket ID, parent ID, and file name for a key path so request handlers can build FSO table keys consistently.

Important APIs and types: The nested `Builder` accepts volume, bucket, key, `OMMetadataManager`, and an optional error message. `build` derives file name with `OzoneFSUtils.getFileName`, volume and bucket IDs from metadata, and parent ID through `OMFileRequest.getParentID`. Instance methods expose all fields plus `getOpenFileName(clientID)` and `getOzonePathKey()`.

Control flow: Building performs all metadata lookups and parent-path resolution, then constructs an immutable-ish object. The path-key methods delegate to metadata manager key-construction helpers.

State and persistence behavior: The object is transient. It describes persistent FSO table key coordinates for `fileTable`, `openFileTable`, and related directory tables.

Dependencies and integration points: FSO file create/commit/lookup/delete request classes can use it to avoid duplicating parent ID and table-key derivation logic.

Risks and test signals: Builder fields are not validated for null before use, so errors surface from metadata manager or path helpers. Tests should cover root-level files, nested parent resolution, missing parent errors, volume/bucket ID lookup failures, open file key construction, and object path key construction.

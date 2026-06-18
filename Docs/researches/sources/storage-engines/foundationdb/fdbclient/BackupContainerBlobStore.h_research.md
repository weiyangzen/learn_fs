# sources/storage-engines/foundationdb/fdbclient/BackupContainerBlobStore.h

Purpose: This header declares the final blobstore backup container class, the object-store implementation of `BackupContainerFileSystem`. It exposes the concrete API needed by the backup container factory while hiding path mapping and bucket/index details.

Important APIs and types: `BackupContainerBlobStore` inherits from `BackupContainerFileSystem` and `ReferenceCounted<BackupContainerBlobStore>`. It stores `Reference<IBlobStoreEndpoint> m_bstore`, backup resource name `m_name`, bucket `m_bucket`, and `isBackup`. Public members include the constructor, reference-count overrides, `getURLFormat`, `validateBackupUrl`, `readFile`, static `listURLs`, `writeFile`, `writeEntireFile`, `deleteFile`, `listFiles`, `create`, `exists`, `deleteContainer`, and `getBucket`. Private helpers `dataPath` and `indexEntry` define the persistent object layout.

Control flow: Callers do not instantiate this class directly except through the backup container factory or listing helper. After construction, all high-level backup operations flow through `BackupContainerFileSystem` APIs and are lowered into blobstore object operations by the `.cpp` implementation. The `friend class BackupContainerBlobStoreImpl` grants private helper access to static actor implementations.

State and persistence behavior: The header documents the state split: all backup data goes into one bucket, while backup-specific path prefixes and index entries determine existence and discovery. `exists` is explicitly defined as checking the index entry, which separates container identity from the presence of individual range/log/snapshot files.

Dependencies and integration points: It includes `AsyncFileBlobStore`, `BackupContainerFileSystem`, and `IBlobStore`, making it the typed bridge between backup filesystem semantics and provider-specific S3/GCS endpoint implementations. `IBackupContainer::getURLFormats` and `openContainer` rely on its static URL helpers.

Risks: The class is `final`, so behavior customization must happen in `IBlobStoreEndpoint` or the common filesystem layer. The `isBackup` flag changes path-prefix semantics, so non-backup use must be careful not to rely on backup index layout. Because encryption fields are inherited from `BackupContainerFileSystem`, constructor arguments must remain aligned with read/write implementations.

Test signals: Header-level contract is covered indirectly by compile-time use in `BackupContainer.cpp`, blobstore container tests, and any provider-specific backup URL tests. Behavioral signals come from the `.cpp` implementation: successful bucket/index creation, encrypted read/write wrapping, and URL validation.

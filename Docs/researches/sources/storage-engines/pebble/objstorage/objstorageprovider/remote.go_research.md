# sources/storage-engines/pebble/objstorage/objstorageprovider/remote.go

Purpose: This file implements the provider's remote/shared object subsystem: catalog initialization, remote storage lookup by locator, shared creator ID management, object creation/opening/removal, ref-marker maintenance, remote cache setup, and tracking of externally named objects.

Important types and functions: `remoteSubsystem` owns the `remoteobjcat.Catalog`, serialized catalog sync mutex, optional `sharedcache.Cache`, and shared creator ID state. `remoteLockedState` holds the pending catalog `Batch`, storage object cache, and external object index. Key methods include `remoteInit`, `SetCreatorID`, `sharedSync`, `sharedCreate`, `remoteOpenForReading`, `remoteSize`, `sharedUnref`, `ensureStorage`, and `GetExternalObjects`.

Control flow: `remoteInit` opens the local remote-object catalog, initializes creator ID if present, opens a shared cache if configured, reconstructs known remote objects, and resolves each object's `remote.Storage`. Creates call `sharedCreate`, which requires a creator ID, creates the remote object, and returns `sharedWritable`; `Finish` later creates the ref marker. Opens optionally verify ref markers in invariant/testing scenarios before reading the backing object. Sync copies and clears the pending catalog batch under provider mutex, then applies it under a catalog sync mutex; failed catalog writes restore the batch.

State and persistence: Persistent state lives in the remote object catalog and remote storage objects/ref markers. In-memory state includes known objects, storage handles, and external-object indexes. Ref-tracked cleanup removes this provider's marker and deletes the backing object only when no markers remain. Protected objects are not unrefed.

Dependencies and integration: It integrates with `remoteobjcat`, `sharedcache`, `remote.StorageFactory`, `objstorage.ObjectMetadata`, and provider metadata bookkeeping in `provider.go`.

Risks and test signals: The main risks are catalog batch ordering, reference-marker races, creator ID initialization, and locator resolution failures. Provider tests cover shared create/remove/reopen, attach, external object tracking, multi-locator attachment, and parallel sync.

# sources/storage-engines/pebble/objstorage/objstorageprovider/remote_backing.go

Purpose: This file defines the binary metadata format used to export and attach remote object backings between providers. It allows shared objects or externally managed objects to be referenced by another DB instance while preserving cleanup/ref-check semantics.

Important APIs and types: `encodeRemoteObjectBacking`, `RemoteObjectBacking`, `CreateExternalObjectBacking`, `decodeRemoteObjectBacking`, and `AttachRemoteObjects` are the main entry points. `remoteObjectBackingHandle` protects an object from cleanup while a backing is held, and unprotects on `Close`. The wire format uses varint tags for creator ID, creator file number, cleanup method, ref-check origin, locator, and custom object name. Unknown tags are skipped if safe and rejected if `tagNotSafeToIgnoreMask` is set.

Control flow: Exporting validates the object is remote, writes creator metadata, adds a ref-check pair for `SharedRefTracking`, and optionally writes locator/custom-name strings. External backings omit normal creator fields and encode a custom object name with `SharedNoCleanup`. Attaching first decodes every backing and resolves storage, then creates local reference markers for ref-tracked objects and verifies the origin provider's marker exists. Only after validation does it add metadata for all objects under the provider mutex.

State and persistence: The encoded backing itself is transient, but attaching persists metadata through the remote catalog on provider `Sync` and may create remote marker objects immediately. The handle's protection state prevents premature unref while another provider is obtaining the backing.

Dependencies and integration: It depends on `objstorage.RemoteObjectBacking`, `remote.Locator`, ref-name helpers, provider metadata updates, and shared remote cleanup.

Risks and test signals: Compatibility of the tag format is critical. Cleanup is incomplete on partial attach failure, noted by TODOs. Tests cover round-tripping, safe/unsafe unknown tags, external object backing creation, attach persistence across reopen, and ref-check corruption behavior through provider tests.

# sources/storage-engines/pebble/objstorage/objstorageprovider/remote_backing_test.go

Purpose: This file validates the remote backing encoding/decoding contract and basic attach persistence for shared and externally named objects.

Important tests: `TestSharedObjectBacking` iterates over `SharedRefTracking` and `SharedNoCleanup` for table and blob file types. It constructs remote metadata, obtains a `RemoteObjectBackingHandle`, checks `Get` before and after `Close`, decodes the buffer into a target file number, and verifies all remote metadata. It also appends safe unknown tags and an unsafe unknown tag to exercise compatibility behavior. `TestCreateSharedObjectBacking` verifies `CreateExternalObjectBacking` produces metadata with locator, custom object name, and no-cleanup. `TestAttachRemoteObjects` attaches a backing, syncs, reopens, and confirms the remote object remains listed with the expected file type and custom name.

Control flow and state: Tests open providers over `vfs.NewMem`, install a simple remote factory, set creator IDs, and use in-memory remote storage. The handle close test confirms backing handles are single-use after `Close` and that protection is released.

Dependencies and integration: The file relies on `supportedFileTypes`, `DefaultSettings`, `Open`, `remote.NewInMem`, and `remote.MakeSimpleFactory`. It is focused on wire-format and catalog integration, not full remote object data I/O.

Risks and test signals: It catches accidental wire-format breaks, missing ref-check fields for ref-tracked objects, and changes to custom-name semantics. It does not test cleanup after partial attach failure or origin ref-marker disappearance; those are covered more broadly in provider data-driven tests.

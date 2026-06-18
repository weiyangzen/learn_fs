# sources/storage-engines/pebble/objstorage/remote/localfs.go

Purpose: This file implements `remote.Storage` on top of a Pebble `vfs.FS`, primarily for testing remote-storage semantics using local files.

Important types and functions: `NewLocalFS` constructs a `localFSStore` rooted at a directory. The store implements `Close`, `ReadObject`, `CreateObject`, `List`, `Delete`, `Size`, and `IsNotExistError`. `localFSReader` adapts a `vfs.File` to `remote.ObjectReader`. `objWriter` wraps a created file and syncs file plus directory on close.

Control flow: Reads open the named object under `dirname`, stat it for size, and return a reader. Reader `ReadAt` normalizes `io.EOF` with a full read to nil, matching `io.ReaderAt` semantics. Creates use `vfs.Create` and return an `objWriter`; closing syncs the file, closes it, and syncs the containing directory. `List` enumerates the directory and filters by prefix; delimiter support is intentionally unimplemented and panics if requested. Delete removes the file and syncs the directory.

State and persistence: Object data is durable local FS state. Store `Close` zeroes the struct; it does not delete objects.

Dependencies and integration: Tests can use it as a remote backend, though most provider tests use `NewInMem`. It depends on `vfs`, `oserror`, and path joining.

Risks and test signals: Risks include lack of delimiter support and path/name assumptions because object names are joined under one directory. The implementation is intentionally simple and not a production cloud storage driver.

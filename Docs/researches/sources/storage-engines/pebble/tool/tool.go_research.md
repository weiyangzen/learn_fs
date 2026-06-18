# Research: sources/storage-engines/pebble/tool/tool.go

## Purpose
`tool/tool.go` defines the public container for Pebble introspection commands and the options used to customize those commands. It is the package's assembly point for DB, find, LSM, manifest, remote catalog, SSTable, WAL, and blob tooling.

## Important APIs, Types, And Functions
`T` holds the root command list, subtool structs, mutable `pebble.Options`, comparer and merger registries, default comparer name, open-error enhancer, open options, DB excise span provider, and remote storage resolver.

Public configuration functions include `Comparers`, `DefaultComparer`, `Mergers`, `FilterDecoders`, `KeySchema`, `KeySchemas`, `OpenOptions`, `FS`, `OpenErrEnhancer`, `WithDBExciseSpanFn`, and `WithDBRemoteStorageFn`. `New` applies defaults and user options, constructs each subtool, and exposes their root commands through `T.Commands`. `ConfigureSharedStorage` mutates remote storage settings after construction.

The file also defines `Comparer` and `Merger` aliases and `debugReaderProvider`, which implements `blob.ReaderProvider` for cache-less debug reads of blob files.

## Control Flow
`New` starts from read-only Pebble options using `vfs.Default`, registers the default comparer, default table filter decoders, and default merger, then applies caller options. It creates all subtools with shared option and registry pointers, so later commands see consistent comparer, merger, filesystem, open options, and remote storage behavior.

## State And Persistence
The code itself does not persist data, but it configures how tools open databases and object storage. `debugReaderProvider.GetValueReader` opens a blob object through `objstorage.Provider`, constructs a `blob.FileReader`, and returns a close hook that closes the reader.

## Dependencies And Integration Points
This is the integration surface for embedding Pebble tooling in higher-level binaries. It couples Cobra command construction, Pebble options, table filter decoders, key schemas, object storage, remote storage, blob reading, and command-specific option injection.

## Risks And Edge Cases
Because most subtools receive pointers to `t.opts`, post-construction mutation can affect command behavior, which is useful but requires care. Custom comparers must be registered before commands attempt pretty formatting or reading custom-comparer tables. `debugReaderProvider.GetValueReader` returns no cleanup for failed `blob.NewFileReader` besides the readable's own lifecycle, so callers rely on underlying constructors to close on error.

## Test Signals
Expected signals are command availability, default read-only behavior, custom comparer/merger registration, Cockroach key schema support, filter decoder registration, remote storage resolution, and blob value debug reads through the provider hook.

# sources/storage-engines/pebble/tool/blob.go

## Purpose
This file implements the `pebble tool blob` command group, currently focused on introspecting blob files and printing their physical layout. It provides command wiring, blob-file opening, reader construction, argument traversal, and layout rendering.

## Important APIs, Types, and Functions
`blobT` holds the Cobra root command, the `layout` subcommand, and shared `*pebble.Options`. `newBlob` constructs the command tree. `newReader` converts a `vfs.File` into an `objstorage.Readable`, derives reader/cache options from Pebble options, and opens a `blob.FileReader`. `foreachBlob` delegates path/file traversal to the shared `processFiles` helper for `.blob` files. `runLayout` is the Cobra command implementation.

## Control Flow
`newBlob` creates a root command named `blob` and a subcommand `layout <blob files>` requiring at least one argument. When `layout` runs, `runLayout` obtains stdout/stderr from Cobra, calls `foreachBlob`, prints each path, calls `r.Layout`, and prints either the layout or an error. `foreachBlob` wraps the callback and reader close function and passes them into `processFiles`, allowing individual file paths or directories to be handled uniformly.

`newReader` first wraps the opened VFS file with `objstorage.NewSimpleReadable`. It builds `ReaderOptions` through `b.opts.MakeReaderOptions`, populates cache options if a cache handle is provided, and parses the filename for a file number to improve cache keying. If `blob.NewFileReader` fails, it combines the open error with closing the readable.

## State and Persistence Behavior
The command is read-only with respect to blob files. It opens files, reads blob layout metadata, and closes readers through `processFiles`. Cache state may be used through `CacheOpts` if the surrounding tool configuration supplies a cache handle; file-number parsing makes cache entries stable for recognized Pebble filenames.

## Dependencies and Integration Points
Dependencies include Cobra, `pebble.Options`, `base.ParseFilename`, `cache.Handle`, `sstableinternal.CacheOptions`, `objstorage`, `blob.FileReader`, and `vfs`. The file integrates with the broader Pebble debug tool framework through `processFiles` and with blob-file internals through `blob.FileReader.Layout`.

## Risks and Edge Cases
The command relies on filename parsing only opportunistically; unrecognized names still open but may lack a useful cache file number. Directory traversal and per-file error behavior are delegated to `processFiles`, so UX consistency depends on that shared helper. `context.TODO()` is used for reader creation, which is acceptable for a command-line debug tool but does not expose cancellation at this layer. Layout errors are printed per file and do not stop processing subsequent files.

## Test Signals
`tool/blob_test.go` runs datadriven tests matching `testdata/blob_*`, which likely exercise command output and errors. Additional signal comes from manual use: `blob layout` should print a path line followed by the decoded layout for each `.blob` input.

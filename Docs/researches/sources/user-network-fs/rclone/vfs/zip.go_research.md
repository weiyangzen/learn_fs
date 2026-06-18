# sources/user-network-fs/rclone/vfs/zip.go

## Purpose
Creates a ZIP archive stream from a VFS directory tree.

## APIs, Flow, And State
`CreateZip(ctx, dir, w)` constructs a `zip.Writer`, recursively walks `Dir.ReadDirAll`, opens each `File`, creates deflated file headers with VFS modtimes, copies contents, and creates stored directory headers before recursing into child directories. Errors are wrapped with operation context, and `fs.CheckClose` preserves close errors.

## Dependencies And Integration
Depends on `archive/zip`, VFS `Dir`/`File` APIs, file handles from `File.Open`, and `io.Copy`. The passed context is currently only part of the signature and not directly used in this implementation.

## Risks And Test Signals
Directory names use `root + e.Path()`, so nested path construction is the main correctness risk. Large files stream through handles and can surface read/cache issues. `zip_test.go` validates many flat files, nested directories, large-file checksum integrity, and root-directory subdirectories.

# sources/storage-engines/pebble/internal/base/filenames.go

Purpose: Centralizes Pebble file/object identifiers, filename construction and parsing, blob file mappings, and diagnostics for unexpected missing files.

APIs and types: `TableNum`, `DiskFileNum`, `BlobFileID`, `BlobReferenceID`, `FileType`, `ObjectInfo`, `ObjectInfoLiteral`, `BlobFileMapping`, `MakeFilename`, `MakeFilepath`, `ParseFilename`, `ParseDiskFileNum`, `MustExist`, `AddDetailsToNotExistError`, and `FileInfo`.

Control flow and state: Formatting functions generate canonical names such as `000123.sst`, `MANIFEST-000123`, `OPTIONS-000123`, `temporary.000123.dbtmp`, `000123.blob`, and `000123.blobmeta`. `ParseFilename` normalizes with `fs.PathBase` and pattern-matches canonical forms. `MustExist` annotates not-exist errors by listing the directory and counting recognized file classes before fataling.

Persistence and dependencies: Encodes the durable naming contract for table, manifest, options, temp, lock, and blob files. Depends on `vfs.FS`, `oserror`, path helpers, redact-safe formatting, and `filepath.Ext` for WAL-ish log counting.

Integration points: Used by DB open, manifest/object storage, blob storage, diagnostics, and directory locking. Blob ID to disk-file mapping is abstracted for manifest blob replacement.

Risks: Filename formats are compatibility-sensitive. `FileTypeLog` construction intentionally panics because WAL naming belongs elsewhere. Blobmeta parsing ignores the offset suffix beyond recognizing the type. Directory diagnostics can race with concurrent file deletion.

Test signals: `filenames_test.go` covers roundtrip formatting/parsing, file type parsing, invalid names, and missing-file diagnostics.

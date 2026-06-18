<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/external_storage/src/local.rs -->
# sources/storage-engines/tikv/components/external_storage/src/local.rs

Purpose: this module implements `ExternalStorage` on top of the local filesystem. It is used for local backup/restore paths and as a testable backend for the trait.

Important APIs and types: `LocalStorage` stores a base `PathBuf` and an `Arc<tokio::fs::File>` opened on the base directory for directory fsync. `LocalStorage::new` opens the base directory and supports a failpoint that can sleep during creation. `tmp_path` creates a random temp filename in the target directory using suffix `tmp<random_hex>`. `url_for` produces `local:///...`.

Control flow: `write` rejects absolute paths and empty names, creates parent directories under the base, logs if overwriting, writes to a random temp file, copies the incoming reader into it, fsyncs the temp file, renames it over the final path, then fsyncs the base directory. `read` opens a standard file and wraps it in `AllowStdIo`, returning an error stream if open fails. `read_part` seeks to an offset and returns a `take(len)` reader. `iter_prefix` either walks a directory fast-path or walks the parent and byte-prefix-filters paths, returning relative `BlobObject` keys. `delete` removes a file if present and fsyncs the base directory.

State and persistence behavior: writes are durable best-effort through temp-file, file fsync, rename, and directory fsync. Existing files can be overwritten to match S3 put semantics. Parent directories are created automatically, and nested relative paths are allowed.

Dependencies and integration points: it uses `tokio::fs`, `walkdir`, `rand`, `futures`, `tikv_util::stream::error_stream`, and the crate's trait types. It is created by `make_local_backend`/`create_storage`.

Risks: the comment notes that `../` components could escape the base path because internal names are assumed controlled by TiKV; this is a path traversal risk if names become user-controlled. Only the base directory is fsynced after nested writes/deletes, not necessarily every newly created parent directory. Prefix matching intentionally compares raw bytes, which avoids `Path::starts_with` pitfalls but must handle platform path encoding carefully.

Test signals: tests cover basic write/read, nested paths, empty and absolute name rejection, URL formatting, and overwrite behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/external_storage/src/local.rs -->

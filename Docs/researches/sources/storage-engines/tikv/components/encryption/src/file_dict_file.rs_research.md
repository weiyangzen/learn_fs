# sources/storage-engines/tikv/components/encryption/src/file_dict_file.rs

Purpose: Persists the plaintext file dictionary mapping data-file paths to `FileInfo`. It supports legacy whole-file rewrite format and a v2 append-log format that can compact back to a base dictionary.

Important APIs and types: `FileDictionaryFile::new` creates and rewrites a dictionary file. `open` recovers existing contents, optionally rewrites, and returns both the persistence handle and recovered `FileDictionary`. `insert`, `remove`, and `sync` mutate the log. `recovery`, `rewrite`, `convert_record_to_bytes`, and `parse_next_record` implement the on-disk format. Internal `LogRecord` distinguishes insert and remove records.

Control flow: V2 files contain an encrypted-file header with raw protobuf `FileDictionary` content followed by log records. Each record has crc32, file-name length, `FileInfo` length, type byte, name bytes, and optional serialized `FileInfo`. Recovery parses the header, loads v1 via `PlaintextBackend` decrypt or v2 directly, then replays records. Incomplete tail records are warned and trimmed by later rewrite; non-tail checksum/type/remove-null failures are treated as unrecoverable and call `set_panic_mark`.

State and persistence: `file_dict`, `removed`, `file_size`, and `append_file` mirror persisted state. V2 `rewrite` writes a random temporary file, syncs it, renames atomically, syncs the base directory, then reopens append mode. Non-log mode rewrites the whole file through `EncryptedFile` with `PlaintextBackend`. Remove-count threshold drives compaction.

Dependencies and integration: Used by `DataKeyManager` to keep file metadata durable before/after filesystem operations. Relies on `EncryptedFile::Header`, protobuf `FileDictionary`/`FileInfo`, crc32, `file_system`, and encryption metrics.

Risks: Mutating comments warn callers to update the in-memory dictionary before persistence. Actual filesystem operations and dictionary updates are not atomic, so higher layers must handle stale dictionary entries. Recovery deliberately tolerates only tail corruption; middle corruption requires manual intervention. `OpenOptions::open(...).unwrap()` in rewrite can panic on unexpected open failure.

Test signals: Tests cover v1/v2 normal insert-remove recovery, missing files, opening existing dictionaries, v1-to-v2 update, v2-to-v1 downgrade, and v2 unreadability through the legacy `EncryptedFile` path.

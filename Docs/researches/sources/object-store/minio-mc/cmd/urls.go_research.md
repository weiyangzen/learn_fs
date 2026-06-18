## sources/object-store/minio-mc/cmd/urls.go

Purpose: defines `URLs`, the source/target transfer descriptor used by copy/sync-style operations. It carries aliases, `ClientContent` records, total counts and sizes, multipart and MD5 flags, checksum type, encryption key database, and non-serialized error/difference fields.

Important APIs are `WithError`, which returns a copy with `Error` set, and `Equal`, which compares source and target URL identity while tolerating nil content sides. State is in-memory operation metadata; JSON output omits `Error` and `ErrorCond`. Dependencies include `probe`, `minio.ChecksumType`, `prefixSSEPair`, and `differType`. Risks are value-copy semantics: callers expecting mutation from `WithError` must use the returned value. `Equal` compares URL structs directly, so canonicalization must happen before population. No direct tests in this subset.

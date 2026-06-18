# sources/sync-backup/syncthing/cmd/dev/stwatchfile/main.go

Purpose: small polling utility that watches one file for existence, size, mtime, and SHA-256 content changes.

Important APIs/types/functions: flag `-period`, main polling loop, and `sha256file`.

Control flow: validates a path, then sleeps for the configured period, stats the file, reports appearance/disappearance, rejects directories, hashes file content, and prints a line whenever size, modification time, or hash changes.

State and persistence behavior: read-only file access. In-memory state tracks last existence, size, mtime, and hash.

Dependencies/integration: standard library only; useful for observing filesystem behavior during Syncthing sync/scanner/debug scenarios.

Risks/test signals: full-file hashing every period can be expensive for large files. It can race with writers and report transient hash errors. Signal is printed change lines with current size, mtime, and hash.

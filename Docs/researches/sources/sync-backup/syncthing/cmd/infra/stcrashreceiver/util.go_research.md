# sources/sync-backup/syncthing/cmd/infra/stcrashreceiver/util.go

Purpose: utility functions for crash receiver user bucketing, report path layout, and gzip file writing.

Important APIs/types/functions: `userIDFor`, `dirFor`, `fullPathCompressed`, and `compressAndWrite`.

Control flow: `userIDFor` chooses `X-Forwarded-For` if present, strips port when possible, combines a fixed salt, address, and current month `YYYYMM`, hashes with SHA-256, and returns the first eight bytes as hex. `dirFor` shards a report ID into two path components. `fullPathCompressed` appends `.gz`. `compressAndWrite` gzip-compresses bytes into a buffer and writes the target file.

State and persistence behavior: `compressAndWrite` writes compressed report data to disk. User IDs rotate monthly and are not persisted here.

Dependencies/integration: used by failure-report storage, Sentry user tagging, and path generation for report URLs.

Risks/test signals: `X-Forwarded-For` may contain multiple IPs and is trusted as-is, so proxy configuration matters. `compressAndWrite` does not create parent directories. Signals are deterministic monthly user IDs for a given source and readable gzip files at expected sharded paths.

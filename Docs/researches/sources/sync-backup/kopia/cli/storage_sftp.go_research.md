<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_sftp.go -->
# sources/sync-backup/kopia/cli/storage_sftp.go

## Purpose
Implements SFTP storage provider flags and option normalization for extra-provider builds.

## Important APIs, Types, And Functions
Key symbols are `storageSFTPFlags`, `Setup`, `getOptions`, `Connect`, and registration. It supports password, keyfile, key data, known hosts file/data, external SSH, embedded credentials, flat layout, SSH command/args, list parallelism, and throttling.

## Control Flow
`getOptions` optionally embeds key and known_hosts file contents, validates one credential source and one host verification source unless external SSH is used, absolutizes file paths, sets sharding, and returns copied options. `Connect` calls `sftp.New`.

## State And Persistence Behavior
Persistent repository config may embed private key and known_hosts data or reference absolute file paths. Backend state lives on the SFTP server.

## Dependencies And Integration Points
Integrates SFTP blob backend, storage registry, sharding helper, file reads, path absolutization, and throttling flags.

## Risks And Edge Cases
Embedding credentials stores private key material in config. External SSH bypasses local credential/known-host validation. Relative paths are converted at connect time, which can surprise users expecting lazy resolution.

## Test Signals
Tests cover option normalization, required auth/known-host checks, embedding failures/success, and flat sharding.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_sftp.go -->

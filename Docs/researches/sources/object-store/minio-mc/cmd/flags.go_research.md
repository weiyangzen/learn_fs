# sources/object-store/minio-mc/cmd/flags.go

Purpose: Defines global CLI flags, encryption flag bundles, checksum flag, and checksum parsing.

Important APIs/types/functions: `envPrefix`, `globalFlags`, `encFlags`, `encCFlag`, `encKSMFlag`, `encS3Flag`, `checksumFlag`, and `parseChecksum`.

Control flow: Flags map command-line/environment values into global config. `parseChecksum` recognizes CRC32, CRC32C, full-object variants, SHA1, SHA256, CRC64NVME, and MD5, enables trailing headers for supported checksum types, and rejects MD5 combined with trailing-header checksums.

State and persistence: Defines CLI metadata only. `parseChecksum` mutates the package-level `useTrailingHeaders` atomic/value defined elsewhere.

Dependencies/integration: Used by most commands through `globalFlags` and by copy through `checksumFlag`.

Risks: Hidden `md5` flag is still active. Checksum aliases and error text must stay aligned with minio-go behavior.

Test signals: No direct tests in this subset.

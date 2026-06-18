# sources/sync-backup/kopia/tools/gettool/autodownload/autodownload.go

Purpose: package `autodownload` is Kopia's embedded replacement for `curl`, `sha256sum`, `gunzip`, `tar`, and `unzip` during tool bootstrapping. It downloads an archive URL, verifies a SHA-256 checksum, and extracts `.tar.gz` or `.zip` contents into a target directory without external binaries.

Important APIs/types/functions: `Download(url, dir, checksum, stripPathComponents)` is the public entry point. `downloadInternal` performs HTTP GET, checksum computation, archive selection, and extraction. `InvalidChecksumError` distinguishes missing and mismatched checksums so callers can regenerate baselines. `untar`, `unzip`, `createFile`, `createSymlink`, and `stripLeadingPath` implement extraction details.

Control flow: `Download` retries `downloadInternal` up to eight times with exponential backoff, removing the output directory between retryable attempts. HTTP 404 and checksum failures are treated as non-retryable. `downloadInternal` buffers the entire response, validates or records the checksum, optionally wraps the reader in gzip, then dispatches to tar or zip extraction by URL suffix.

State/persistence: it creates/removes files under the caller-provided output directory, preserves archive file modes and modification times for regular files, and records discovered checksums by mutating the supplied checksum map. Extraction uses `os.OpenRoot`, which reduces path traversal exposure by operating relative to a directory root.

Dependencies/integration: depends on Go archive, gzip, HTTP, crypto, and `github.com/pkg/errors`. It is used by Kopia `tools/gettool` and `tools.mk` to install pinned build tools.

Risks/test signals: zip downloads are buffered fully in memory. Archive support is intentionally narrow, and unsupported entries fail the install. Checksums are keyed by full URL, so URL-template changes require checksum regeneration. There are no local tests in this subset; coverage is indirect through gettool checksum verification targets.

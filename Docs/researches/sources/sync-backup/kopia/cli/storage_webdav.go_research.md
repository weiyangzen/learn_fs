<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_webdav.go -->
# sources/sync-backup/kopia/cli/storage_webdav.go

## Purpose
Implements WebDAV storage provider flags for extra-provider builds.

## Important APIs, Types, And Functions
Defines `storageWebDAVFlags`, `Setup`, `Connect`, and registration. Flags include URL, flat layout, username/password with environment overrides, list parallelism, atomic writes, and throttling.

## Control Flow
Connect copies options, prompts for a WebDAV password when username is provided without password, sets directory sharding, and calls `webdav.New`.

## State And Persistence Behavior
Persistent config stores WebDAV URL, optional credentials, atomic-write assumption, and sharding. Backend data lives on WebDAV storage.

## Dependencies And Integration Points
Integrates WebDAV blob backend, storage registry, password prompting, env-name namespacing, sharding helper, and throttling.

## Risks And Edge Cases
Prompting uses `os.Stdout` directly and terminal stdin from `askPass`, which can fail in noninteractive use. Atomic writes are a provider assumption that can affect repository safety.

## Test Signals
Tests should cover password prompt path, env password path, flat/version sharding, atomic writes, and backend option construction.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_webdav.go -->

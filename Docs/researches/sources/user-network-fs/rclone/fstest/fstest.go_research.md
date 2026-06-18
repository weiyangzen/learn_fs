# sources/user-network-fs/rclone/fstest/fstest.go

## Purpose
This package provides shared test utilities for rclone filesystem/backend tests. It initializes test configuration, creates random remotes, builds expected file items, verifies listings and metadata, handles eventual consistency, and cleans up test remotes.

## Important APIs, Flow, and State
Global flags include `RemoteName`, `Verbose`, dump flags, `Individual`, `LowLevelRetries`, `UseListR`, `SizeLimit`, and `ListRetries`. `Initialise` configures password behavior, config path, accounting, logging, retries, and fast-list behavior. `Item` stores expected path, hashes, modtime, and size; `NewItem` computes hashes. `Items` tracks expected object matches. Listing helpers include `CheckListingWithRoot`, precision variants, `CheckItems`, and `CompareItems`. Remote helpers include `LocalRemote`, `RandomRemoteName`, `RandomRemote`, and `Purge`. Discovery and metadata helpers include `NewObject`, `NewDirectoryRetries`, `NewDirectory`, `CheckEntryMetadata`, `CheckDirModTime`, and `Gz`.

`CheckListingWithRoot` calls `walk.GetAll` with retries and sleeps to tolerate eventual consistency, optionally flushing directory caches. `RandomRemote` creates a local temp path or random remote child and returns a finalizer. `Purge` tries backend purge first, then recursively removes objects and directories in reverse order.

## Dependencies, Risks, and Test Signals
Dependencies include `fs`, `accounting`, config/configfile, `hash`, `log`, `walk`, `random`, `testy`, and Unicode normalization. Because these helpers sit under many tests, changes can cause broad false positives or negatives. Edge cases include macOS Unicode normalization, empty directory limitations, eventual consistency, unsupported directory modtimes, Windows CI timestamp precision, cleanup error isolation, and safe random remote naming. This infrastructure is exercised extensively by sync, transform, backend, and listing tests.

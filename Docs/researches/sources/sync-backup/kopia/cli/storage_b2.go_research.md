<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_b2.go -->
# sources/sync-backup/kopia/cli/storage_b2.go

## Purpose
Registers the deprecated B2 storage provider CLI wrapper.

## Important APIs, Types, And Functions
Defines `storageB2Flags`, `Setup`, `Connect`, and `init`. It maps bucket, key ID, key, prefix, and throttling flags into `b2.Options`.

## Control Flow
Connect simply calls `b2.New` with the collected options and create/read mode.

## State And Persistence Behavior
Persistent repository storage configuration is written by higher-level repository connect/create logic; this file stores only transient parsed flags.

## Dependencies And Integration Points
Integrates B2 blob backend, storage provider registry, Kingpin, environment namespacing, and throttling flags. It is compiled only when extra providers are enabled.

## Risks And Edge Cases
The provider is marked deprecated. Credentials are required and may be provided via env or CLI. Backend handles most validation.

## Test Signals
Tests should verify provider registration under extra-provider builds, required flags/env overrides, and throttling option propagation.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_b2.go -->

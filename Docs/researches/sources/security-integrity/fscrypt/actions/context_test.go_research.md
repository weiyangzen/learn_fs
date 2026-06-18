# sources/security-integrity/fscrypt/actions/context_test.go

## Purpose
Provides package-wide integration test setup for the `actions` package by creating a real test mount context, config file, and fscrypt metadata directory.

## APIs and Control Flow
`setupContext` obtains `util.TestRoot`, redirects `ConfigFileLocation`, verifies `NewContextFromMountpoint` fails without a config file, creates a config, creates a context, and sets up the mount with world-writable metadata. `TestMain` initializes `testContext`, skips cleanly on `util.ErrSkipIntegration`, runs package tests, and cleans up config and metadata.

## State, Dependencies, and Integration
This file is the shared fixture for protector, policy, recovery, and hashing-adjacent action tests. It mutates real filesystem metadata through `filesystem.Mount.Setup` and `RemoveAllMetadata`.

## Risks and Test Signals
Because it uses integration infrastructure, test results depend on available filesystem encryption support. Cleanup is centralized, but package globals and real mount metadata can leak if a process exits abruptly.

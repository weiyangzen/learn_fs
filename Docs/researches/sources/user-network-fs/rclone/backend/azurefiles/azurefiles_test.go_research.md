# Research: sources/user-network-fs/rclone/backend/azurefiles/azurefiles_test.go

## Purpose
This file wires the Azure Files backend into rclone's generic filesystem integration test suite.

## Important APIs, Types, and Functions
- `TestIntegration` creates a nil `*Object` marker and calls `fstests.Run` with `RemoteName: "TestAzureFiles:"`.

## Control Flow
The generic fstests runner drives backend operations through the advertised rclone interfaces. The file does not customize chunk sizes, features, tiers, or extra config.

## State and Persistence Behavior
When run with a configured `TestAzureFiles:` remote, fstests create, list, update, read, copy/move where supported, and remove files/directories in the Azure File Share.

## Dependencies and Integration Points
The file depends only on Go testing and rclone `fstests`. It indirectly exercises `azurefiles.go` methods and may invoke `Fs.InternalTest` from `azurefiles_internal_test.go`, though that internal auth test skips.

## Risks and Edge Cases
- Coverage depends on live Azure Files credentials and an available test share.
- No backend-specific options are varied, so unknown-size uploads, OpenWriterAt, and some copy/move edge cases may not receive focused coverage here.
- Failures are likely integration/environment sensitive.

## Test Signals
This is the main automated conformance signal for the Azure Files backend against rclone's filesystem contract.

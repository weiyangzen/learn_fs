# sources/user-network-fs/rclone/backend/cloudinary/cloudinary_test.go

## Purpose
This file provides the Cloudinary backend integration test harness. It validates the backend through rclone's generic filesystem test suite rather than through direct unit tests of Cloudinary-specific helpers.

## Important APIs, types, and functions
`TestIntegration` calls `fstests.Run` with `RemoteName` set to `TestCloudinary:`, `NilObject` set to `(*cloudinary.Object)(nil)`, and `SkipInvalidUTF8` enabled. The test injects one extra config item: `eventually_consistent_delay=7`, matching Cloudinary's eventual-consistency characteristics.

## Control flow
When the test runs in an environment with a configured `TestCloudinary` remote, the shared rclone test suite creates, updates, lists, reads, removes, and checks objects/directories through the registered backend. All behavior is exercised through public `fs.Fs` and `fs.Object` interfaces, not direct package internals.

## State and persistence behavior
The test writes to a real Cloudinary remote and therefore depends on external credentials, network availability, Cloudinary account state, and cleanup behavior from `fstests`. The configured delay is intended to reduce false negatives caused by delayed Cloudinary search/list consistency.

## Dependencies and integration points
It depends on the `cloudinary` backend package for the nil object type and on `github.com/rclone/rclone/fstest/fstests` for the behavioral contract. The test is a signal that the backend is expected to satisfy broad rclone semantics despite Cloudinary-specific limitations such as unsupported modtime precision and empty-file uploads.

## Risks and edge cases
Because this is only an integration harness, CI without a configured Cloudinary remote may skip or fail depending on rclone test setup. It does not isolate Cloudinary API error handling, name encoding, media extension adjustment, public ID determinism, or retry-after parsing. Failures may be slow due to the 7-second consistency delay.

## Test signals
The presence of a generic `fstests.Run` means common rclone operations are covered at high level. Local deterministic unit coverage for backend helper functions is absent in this file.

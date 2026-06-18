# sources/user-network-fs/rclone/cmd/selfupdate/verify_test.go

## Purpose

This test file validates self-update checksum verification against checked-in fixture data.

## Important APIs, Types, and Functions

`TestVerify` reads `testdata/verify/SHA256SUMS`, decodes the known archive SHA-256 hex string, and calls `verifyHashsumDownloaded` across four subtests.

## Control Flow

The success case verifies the fixture signature and hash. `BadSig` flips one byte in the signed data and expects an invalid signature error, then restores it. `BadSum` flips one byte in the expected digest and expects an archive hash mismatch. `BadName` asks for a non-existent archive and expects the hash lookup path to fail.

## State and Persistence Behavior

The test mutates local byte slices in memory and restores them between subtests. It reads immutable fixtures only.

## Dependencies and Integration Points

It depends on build tag `!noselfupdate`, the local `testdata/verify` release-like files, `encoding/hex`, and testify assertions.

## Risks and Test Signals

Coverage is focused and valuable for signature and digest regression. It does not exercise the networked `verifyHashsum` downloader, malformed clearsign blocks, unsigned trailing data, keyring parse failure, or multiple archive checksum rows.

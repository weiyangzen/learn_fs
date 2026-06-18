<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_sftp_test.go -->
# sources/sync-backup/kopia/cli/storage_sftp_test.go

## Purpose
Unit tests for SFTP option normalization and validation.

## Important APIs, Types, And Functions
`TestSFTPOptions` builds cases for keyfile/known_hosts path absolutization, missing files during embedding, missing auth or known-host data, embedding file contents, flat sharding, and password authentication. `mustFileAbs` provides expected absolute paths.

## Control Flow
Each case calls `storageSFTPFlags.getOptions(2)` and compares the resulting `sftp.Options` or expected error substring.

## State And Persistence Behavior
Test state is limited to temporary key and known_hosts files. No network/SFTP server is contacted.

## Dependencies And Integration Points
Integrates the SFTP CLI flag struct, sharded directory options, file embedding, and testify assertions.

## Risks And Edge Cases
Expected structs must track backend option defaults. The test does not cover external SSH mode, SSH args/env, format version 1 sharding, or throttling.

## Test Signals
Strong signal for credential and host-verification validation, which is the main local behavior in `storage_sftp.go`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_sftp_test.go -->

# sources/user-network-fs/rclone/backend/smb/smb_test.go

## Purpose

This file runs rclone's generic integration tests against SMB remotes, including NTLM and Kerberos configurations.

## Important APIs, Types, and Functions

`TestIntegration` uses `TestSMB:rclone`. `TestIntegration2` uses `TestSMBKerberos:rclone` with temporary `KRB5_CONFIG` and `KRB5CCNAME`. `TestIntegration3` uses `TestSMBKerberosCcache:rclone` and injects an extra `kerberos_ccache` config value. All pass `NilObject: (*smb.Object)(nil)`.

## Control Flow

Each test calls `fstests.Run`. Kerberos tests skip when `-remote` is supplied, then set temp env/config paths before invoking the suite. The third test also sets `RCLONE_TEST_CUSTOM_CCACHE_LOCATION`.

## State and Persistence Behavior

State is confined to temporary directories and environment variables plus the configured remote test shares. The integration suite creates and removes remote test data.

## Dependencies and Integration Points

It depends on `fstest` and `fstests`, plus external SMB test remotes. It validates the public backend package from `smb_test`.

## Risks and Edge Cases

These tests require external SMB infrastructure and valid Kerberos setup. They do not directly unit-test connection pooling, idle drain, or writer-at behavior, though generic operations exercise them indirectly.

## Test Signals

Passing tests indicate the backend works with normal credentials, default Kerberos ccache discovery, and custom ccache configuration.

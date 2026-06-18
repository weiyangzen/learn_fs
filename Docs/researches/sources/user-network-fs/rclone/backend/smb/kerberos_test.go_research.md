# sources/user-network-fs/rclone/backend/smb/kerberos_test.go

## Purpose

This file unit-tests SMB Kerberos credential cache path resolution and reload behavior.

## Important APIs, Types, and Functions

`TestResolveCcachePath` covers `FILE:` and `DIR:` environment forms, unsupported schemes, direct paths, and default `/tmp/krb5cc_<uid>` fallback. `TestKerberosFactory_GetClient_ReloadOnCcacheChange` creates a temporary ccache and injects mock `loadCCache`, `newClient`, and `loadConfig` functions into a `KerberosFactory`.

## Control Flow

Each path-resolution subtest sets `KRB5CCNAME`, calls `resolveCcachePath`, and checks the result or expected error. The reload test calls `GetClient` twice without file changes to confirm cache reuse, then modifies the ccache after a sleep to force mtime change and confirms the loader is called again.

## State and Persistence Behavior

Tests write temporary files/directories and environment variables scoped by `testing.T`. Factory caches live only for the test instance.

## Dependencies and Integration Points

It uses gokrb5 types only as mock return values, plus `testify/assert`. It directly tests unexported package helpers because it is in package `smb`.

## Risks and Edge Cases

The mtime test sleeps one second to avoid filesystem timestamp granularity issues, which can slow the suite and still depends on platform behavior. It does not validate real Kerberos config parsing or ticket usability.

## Test Signals

Passing tests indicate cache invalidation and ccache URI parsing behave as expected. Additional useful cases would cover cached-error reuse and `KRB5_CONFIG` selection.

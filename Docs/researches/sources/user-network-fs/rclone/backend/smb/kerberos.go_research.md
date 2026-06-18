# sources/user-network-fs/rclone/backend/smb/kerberos.go

## Purpose

`kerberos.go` provides Kerberos client construction and cache handling for SMB authentication.

## Important APIs, Types, and Functions

`KerberosFactory` stores `sync.Map` caches for clients, errors, and ccache mtimes plus injectable loaders for credential caches, clients, and krb5 config. `NewKerberosFactory` wires default gokrb5 functions. `GetClient` resolves a ccache path, stats it, reuses cached client/error when mtime is unchanged, otherwise reloads config and credentials and creates a new client. `resolveCcachePath` handles explicit paths, `KRB5CCNAME`, `FILE:` and `DIR:` schemes, and `/tmp/krb5cc_<uid>` fallback. `defaultLoadKerberosConfig` loads `KRB5_CONFIG` or `/etc/krb5.conf`.

## Control Flow

SMB dialing calls `NewKerberosFactory().GetClient`. Path resolution happens first. If the ccache file mtime matches cached state, cached error or client is returned. Otherwise the factory loads krb5 config, loads the ccache, creates a gokrb5 client, updates caches, and clears stale errors.

## State and Persistence Behavior

Factory state is in-memory cache. Persistent inputs are ccache files, `DIR:` primary files, and krb5 config files. This file never writes credentials.

## Dependencies and Integration Points

It depends on `jcmturner/gokrb5/v8` client/config/credentials packages and OS user/env/path helpers. `connpool.go` integrates the returned client into `smb2.Krb5Initiator`.

## Risks and Edge Cases

Because `connpool.go` creates a new factory for each dial, these caches may not persist across dials unless reused elsewhere. `DIR:` mode depends on a readable `primary` file. Unsupported ccache schemes fail. Cached errors persist until ccache mtime changes, so config-only fixes may not be retried if mtime is unchanged.

## Test Signals

`kerberos_test.go` validates path resolution and reload-on-mtime-change with injected loaders. Integration tests cover Kerberos SMB remotes using default and custom ccache locations.

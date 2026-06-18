# sources/object-store/minio-mc/cmd/client-admin.go

## Purpose

`client-admin.go` constructs and caches MinIO admin clients and anonymous admin clients from aliases.

## Important APIs, Types, and Functions

`NewAdminFactory` returns a closure that caches `*madmin.AdminClient` by config hash under a mutex. `newAdminClient` expands aliases and builds a signed admin client. `newAnonymousClient` expands aliases and builds an unsigned `madmin.AnonymousClient`. `s3AdminNew` is the package-level cached factory.

## Control Flow

The admin factory parses host URL, computes a config hash, checks the cache, builds transport and credential chain, creates `madmin.NewWithOptions`, sets custom transport and app info, caches it, and returns it. `newAdminClient` rejects raw URLs without alias config, builds an S3 config, and calls the factory. `newAnonymousClient` similarly rejects unknown URLs, parses TLS mode, creates an anonymous client, installs a custom transport, and wraps debug tracing when enabled.

## State and Persistence Behavior

The factory holds an in-memory client cache for the process lifetime. No local files are written. Alias config is read through `expandAlias`.

## Dependencies and Integration Points

It integrates with alias resolution, `Config` transport/credentials helpers, `madmin-go`, minio-go credential chains, ieproxy, TLS/root CA globals, custom dialers, HTTP tracing, app metadata, and global debug/insecure settings.

## Risks and Edge Cases

Cache invalidation depends entirely on `getConfigHash`; changed global state not included in the hash could reuse stale clients. Raw URLs are intentionally rejected for admin operations. Anonymous transport constructs TLS config from global roots and insecure flag.

## Test Signals

Tests should cover cache reuse by equivalent config, cache miss for changed config, invalid alias/raw URL rejection, custom transport installation, app info propagation, and anonymous client TLS mode.

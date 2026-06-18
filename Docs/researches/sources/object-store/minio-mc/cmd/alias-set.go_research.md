# sources/object-store/minio-mc/cmd/alias-set.go

## Purpose

`alias-set.go` implements `mc alias set`, creating or updating local aliases and probing S3 signature compatibility when the API signature is not explicitly provided.

## Important APIs, Types, and Functions

`aliasSetFlags` defines path and API options. `checkAliasSetSyntax` validates alias, URL, credentials, API, and path or deprecated lookup. `setAlias` writes config. `probeS3Signature` tries S3v4 then S3v2 against a random probe bucket. `BuildS3Config` builds and optionally probes a `Config`. `fetchAliasKeys` reads credentials from args, prompts, or stdin. `configurePeerCertificate` injects a trusted peer certificate into transport roots.

## Control Flow

The handler normalizes deprecated lookup into path mode, fetches credentials, validates syntax, creates a cancellable context, optionally prompts to trust a self-signed certificate, builds/probes S3 config, saves the alias with resolved URL/signature/path, sets operation `set` or deprecated `add`, and prints output.

## State and Persistence Behavior

The command persists alias credentials in the local MinIO Client config. It may also mutate in-memory TLS root CA pools or transport settings to trust a peer certificate. It contacts the remote endpoint during signature probing unless API is specified.

## Dependencies and Integration Points

It integrates with S3 config creation, minio-go error responses, prompt trust logic, TLS transport helpers, config load/save, validation helpers, and global networking/debug settings.

## Risks and Edge Cases

Credentials can leak through args or JSON output. Signature probing treats `BucketDoesNotExist` and `AccessDenied` as success, which is intentional but depends on server behavior. The random probe bucket uses `math/rand` seeded by time, not crypto randomness, but only for a probe name. Peer certificate trust mutates shared CA state in some branches.

## Test Signals

Tests should cover credential prompt paths, validation failures, explicit API bypassing probe, S3v4-to-S3v2 fallback, self-signed certificate configuration, deprecated lookup mapping, and saved config fields.

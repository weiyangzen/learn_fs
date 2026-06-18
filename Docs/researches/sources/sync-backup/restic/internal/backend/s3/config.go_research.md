<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/s3/config.go -->
# sources/sync-backup/restic/internal/backend/s3/config.go

## Purpose
Parses and registers S3-compatible backend configuration and applies region environment defaults.

## Important APIs, Types, And Functions
Config, NewConfig, ParseConfig, createConfig, ApplyEnvironment, and option registration are key.

## Control Flow
ParseConfig supports s3:http(s) URL forms plus s3:// and s3: endpoint/bucket/prefix forms, cleans prefixes, and records HTTP usage. ApplyEnvironment fills Region from AWS_DEFAULT_REGION when unset.

## State And Persistence Behavior
Config stores endpoint, bucket, prefix, credentials/testing fields, storage class, restore settings, retry/listing options, and connection count.

## Dependencies And Integration Points
Depends on net/url, os, path, strings, time, internal/backend/errors/options.

## Risks And Edge Cases
Parsing assumes endpoint and bucket split semantics; empty endpoint is rejected while some bucket validation is deferred to S3 operations.

## Test Signals
config_test.go covers many URL forms and invalid endpoint cases.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/s3/config.go -->

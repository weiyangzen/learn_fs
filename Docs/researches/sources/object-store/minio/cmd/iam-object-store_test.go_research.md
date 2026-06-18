# sources/object-store/minio/cmd/iam-object-store_test.go

## Purpose

`iam-object-store_test.go` verifies `splitPath`, the helper used by `IAMObjectStore.listAllIAMConfigItems` to classify walked IAM config objects into top-level buckets while preserving the rest of the entity path.

## Important Tests And Control Flow

`TestSplitPath` covers regular one-level paths such as `users/tester.json`, nested group paths, `format.json`, and policydb paths. The important cases are `policydb/sts-users/...` and `policydb/groups/...` entries whose entity names include one or more `/` characters, as LDAP DNs or other external identifiers can contain slashes. With `secondIndex=true`, `splitPath` returns the list key as `policydb/sts-users/` or `policydb/groups/` and leaves the entire slash-containing entity filename in the item string.

## State, Dependencies, Integration, Risks, And Signals

The test depends only on `testing`. It guards against a subtle IAM data-loss/regression risk: splitting policydb entries at the first slash would corrupt user/group names and prevent policy mappings from loading or reconciling correctly. The test does not cover object walking, config decryption, concurrent loaders, or expired-credential purge; those remain integration concerns for `IAMObjectStore`.

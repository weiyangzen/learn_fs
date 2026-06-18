# sources/object-store/minio/cmd/iam-etcd-store_test.go

## Purpose

`iam-etcd-store_test.go` tests the path-normalization helper used when deriving IAM entity names from etcd keys.

## Important Tests And Control Flow

`TestExtractPrefixAndSuffix` supplies group-style and nested config paths such as `config/iam/groups/foo.json`, `config/iam/groups/./foo.json`, and `config/iam/groups/foo/config.json`. It asserts that `extractPathPrefixAndSuffix` removes the configured prefix, removes either `.json` or `config.json`-style suffixes, cleans the path, and returns `foo`.

## State, Dependencies, Integration, Risks, And Signals

The test has no external dependencies beyond `testing`. It gives direct coverage for a small but important helper used by etcd bulk loaders and list-to-name conversion. The gap is that it does not spin up etcd, verify encryption/decryption, expired credential deletion, prefix listing, policy mapping loading, or watcher retry semantics. It also does not cover entity names containing slashes in policydb paths; analogous object-store path splitting is covered in `iam-object-store_test.go`.

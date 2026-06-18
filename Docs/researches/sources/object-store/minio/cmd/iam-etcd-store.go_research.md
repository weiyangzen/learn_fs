# sources/object-store/minio/cmd/iam-etcd-store.go

## Purpose

`iam-etcd-store.go` implements `IAMStorageAPI` over etcd. It stores IAM identities, groups, policies, and policy mappings under the same logical key prefixes used by the object-store backend, handles optional KMS encryption/decryption, loads bulk IAM data from prefix scans, and exposes an etcd watch stream for live cache updates.

## Important APIs, Types, And Control Flow

`IAMEtcdStore` embeds an `iamCache`, protects it with an `RWMutex`, records the active `UsersSysType`, and holds an `etcd.Client`. Its lock/rlock methods return the cache to satisfy `IAMStorageAPI`. `saveIAMConfig` marshals JSON, encrypts when `GlobalKMS` is configured using a context based on `.minio.sys` metadata paths, and calls `saveKeyEtcd`. `loadIAMConfig`, `loadIAMConfigBytes`, and `getIAMConfig` read keys, decrypt through shared `decryptData`, and unmarshal using jsoniter.

Bulk loaders use etcd prefix scans with a 30 second `defaultContextTimeout`. Policies are loaded from `iamConfigPoliciesPrefix` by `loadPolicyDocs`, parsing each `PolicyDoc`. Users are loaded by user type from regular, service-account, or STS prefixes; expired identities and invalid temporary credentials are deleted along with their policy mappings. Groups are first listed with keys-only prefix scans, normalized by `extractPathPrefixAndSuffix`, then loaded individually. Policy mappings are loaded from user, STS, service-account, or group policydb prefixes into `xsync.MapOf`.

`watch` starts a goroutine that watches a prefix with keys-only events, retries after watch channel closure or watch errors, and emits `iamWatchEvent` values for create/modify and delete events.

## State, Dependencies, Integration, Risks, And Tests

Persistent state is etcd key/value data under IAM config prefixes, optionally encrypted. Integration is through `IAMStoreSys.LoadIAMCache`, notification handlers, and `IAMSys.periodicRoutines` watcher support. Dependencies include etcd v3, mvcc key values, MinIO config/KMS helpers, jsoniter, and xsync maps. Risks include path extraction for identities containing slashes, expensive per-group reloads after key-only scans, best-effort deletion of expired credentials, watch goroutine lifetime/channel blocking, and consistency around TTL options passed to lower-level etcd save helpers. `iam-etcd-store_test.go` covers prefix/suffix extraction normalization, but most behavior relies on shared IAM store tests or integration tests with etcd.

# sources/object-store/minio/cmd/iam-object-store.go

## Purpose

`iam-object-store.go` implements `IAMStorageAPI` using MinIO's own object layer, storing IAM configuration objects under the internal metadata bucket. It is the normal non-etcd persistence backend for policies, users, service accounts, STS accounts, groups, and policy mappings.

## Important APIs, Types, And Control Flow

`IAMObjectStore` embeds an `iamCache`, protects it with an `RWMutex`, records the active user-system type, and holds an `ObjectLayer`. `saveIAMConfig` marshals JSON with jsoniter, encrypts with `GlobalKMS` when configured, and writes with `saveConfig`. `decryptData` returns plaintext directly when valid UTF-8, otherwise attempts legacy `madmin.DecryptData`, KMS decrypt with `.minio.sys/<path>` context, and KMS decrypt with raw object path context for compatibility. Load helpers read config bytes and metadata so old policy formats can derive create/update dates from object `ModTime`.

User loading normalizes missing access keys, deletes expired identities and their mappings, extracts JWT claims for temporary/service credentials, and carries comments into descriptions. The object backend has concurrency helpers for users, policies, and policy mappings using `errgroup.WithNErrs`. `listIAMConfigItems` walks the metadata bucket and returns object names trimmed relative to a prefix.

The high-impact method is `loadAllFromObjStore`: it lists all IAM config items once, buckets them by top-level list keys, loads policy documents and user mappings in batches of 32, loads regular users/groups for MinIO user mode, loads group/user policy mappings, loads service accounts, handles STS parent policy mappings for service accounts, builds user-group memberships, purges expired STS users from disk while tolerating errors, and replaces STS maps in cache. The custom `splitPath` treats `policydb/*` specially by splitting on the second slash so slash-containing LDAP/OIDC DNs remain intact.

## State, Dependencies, Integration, Risks, And Tests

Persistent state is object data under `.minio.sys/config/iam/`, optionally encrypted and version/format compatible across releases. Dependencies include `ObjectLayer.Walk`, config read/write/delete helpers, KMS, madmin legacy decryption, logger timing, jsoniter, errgroup, and xsync maps. Risks include UTF-8 plaintext detection around encrypted data, legacy decryption compatibility, object-list staleness during concurrent IAM writes, slash-containing identity path handling, ignored errors while purging expired STS credentials, and batch/concurrency behavior on large IAM stores. `iam-object-store_test.go` covers `splitPath`, especially policydb entries containing slash-heavy LDAP DNs.

# sources/object-store/minio/cmd/iam-store.go

## Purpose

`iam-store.go` is the shared high-level IAM storage layer above both object-store and etcd backends. It defines IAM on-disk paths and data models, owns the in-memory `iamCache`, loads/replaces cache state, and implements the administrative operations for policies, policy mappings, users, groups, service accounts, STS accounts, and notification-driven cache updates.

## Important APIs, Types, And Control Flow

Path helpers build canonical storage locations under `config/iam`: users, service accounts, groups, policies, STS accounts, and policydb maps. Core data models are `UserIdentity`, `GroupInfo`, `MappedPolicy`, and `PolicyDoc`. `PolicyDoc.parseJSON` accepts both the newer document wrapper and older raw `policy.Policy` format. `iamCache` stores policy docs, regular/service users, STS users, user/group/STS policy maps, groups, and reverse user-group memberships. `IAMStorageAPI` is the backend contract implemented by object-store and etcd stores.

`LoadIAMCache` builds a fresh cache, delegates to the optimized object-store full loader when available, otherwise loads policies, users, groups, mappings, and service accounts sequentially from the backend. It then replaces the live cache only if no local cache mutation happened after loading began, unless this is the first load. This prevents stale periodic refreshes from overwriting newer admin changes. STS policy maps are merged because periodic reloads are partial.

Group methods validate regular users, prevent temp/service accounts from group membership, persist `GroupInfo`, and update reverse membership maps. Policy methods attach, detach, set, delete, list, merge, and hot-load missing policies. Delete flows prevent deletion of policies still mapped to regular users/groups and update maps after notification deletes. User methods cover create/update/delete, status/secret changes, notification reloads, derived credential cleanup, and singleflight `LoadUser` for demand-loading individual identities. Service-account methods create/update/list/delete credentials, rewrite session-token claims when policy/status/secret changes, enforce expiration bounds, and hide secret/session values in list responses. STS methods set temporary users with TTL, revoke tokens by parent/type, list accounts, and purge/update derived credentials.

## State, Dependencies, Integration, Risks, And Tests

State spans persistent IAM config plus a mutable process cache protected by backend locks and xsync maps. Dependencies include MinIO auth credentials, madmin DTOs, policy parsing/merging, OpenID role metadata, environment flags, singleflight, errgroup, jsoniter, and JWT claim extraction. Integration points are `IAMSys`, admin APIs, STS flows, site replication hooks, LDAP/OIDC cleanup, and backend notification handlers. Risks include stale cache replacement timing, partial STS reload semantics, policy map consistency after deletes, disabled-group behavior denying access, derived credential cleanup when parents disappear, lock ordering around backend calls, and JWT claim extraction with multiple signing keys. Tests in this subset cover backend path helpers; broader IAM behavior is expected to be exercised by higher-level IAM/admin/STSes tests outside the listed files.

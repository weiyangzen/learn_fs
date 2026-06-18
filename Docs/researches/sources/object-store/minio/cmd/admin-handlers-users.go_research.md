# sources/object-store/minio/cmd/admin-handlers-users.go

## Purpose
`admin-handlers-users.go` is the main MinIO admin IAM handler file. It implements user, group, policy, service-account/access-key, temporary-account, token-revocation, account-info, and IAM import/export endpoints under `/minio/admin/v3`. It is the HTTP boundary between authenticated admin clients and `globalIAMSys`, with explicit checks for internal users, LDAP users, OpenID-derived credentials, service accounts, STS credentials, policy mappings, and site-replication hooks.

## Important APIs, Types, And Functions
User and group handlers include `RemoveUser`, `ListBucketUsers`, `ListUsers`, `GetUserInfo`, `UpdateGroupMembers`, `GetGroup`, `ListGroups`, `SetGroupStatus`, `SetUserStatus`, and `AddUser`.

Access-key and service-account handlers include `TemporaryAccountInfo`, `AddServiceAccount`, `UpdateServiceAccount`, `InfoServiceAccount`, `ListServiceAccounts`, `DeleteServiceAccount`, `ListAccessKeysBulk`, and `InfoAccessKey`. `commonAddServiceAccount` centralizes encrypted request parsing, target-user defaulting, expiration normalization, duration-condition injection, self-service versus admin permission checks, and session policy parsing for service-account creation.

Policy handlers include `InfoCannedPolicy`, `ListBucketPolicies`, `ListCannedPolicies`, `RemoveCannedPolicy`, `AddCannedPolicy`, deprecated `SetPolicyForUserOrGroup`, modern `ListPolicyMappingEntities`, and `AttachDetachPolicyBuiltin`. `setReqInfoPolicyName` annotates audit request info with policy names.

IAM import/export uses constants for `iam-assets/policies.json`, `users.json`, `groups.json`, `svcaccts.json`, `user_mappings.json`, `group_mappings.json`, and `stsuser_mappings.json`, plus `iamExportFiles`, `ExportIAM`, `ImportIAM`, `ImportIAMV2`, and shared `importIAM`.

## Control Flow
Most mutating handlers follow a common structure: validate server initialization and admin signature/permission, parse route variables and encrypted or plain JSON payload, reject invalid identity classes, call `globalIAMSys`, return an madmin-compatible response, then emit a site-replication IAM change hook when appropriate.

User handlers forbid root-user removal, self-removal, temporary-user modification through regular-user APIs, service-account modification through user APIs, and internal user creation when LDAP is enabled. `AddUser` supports self password updates only through a deny-only permission check, rejects invalid UTF-8 and leading/trailing-space access keys, decrypts `madmin.AddOrUpdateUserReq`, and persists through `globalIAMSys.CreateUser`.

Group handlers reject temporary credentials and root credentials as members. Adding a new group rejects names with leading/trailing spaces, and internal group manipulation is disabled in LDAP mode. Status and membership changes emit `madmin.SRIAMItemGroupInfo` replication events.

Service-account creation first parses an encrypted `madmin.AddServiceAccountReq` in `commonAddServiceAccount`. It truncates expiration to seconds, rejects access keys with leading/trailing spaces, validates client-side request shape server-side, injects `svc:DurationSeconds` into condition values when expiration is set, and uses `DenyOnly` for self-service creation. `AddServiceAccount` then resolves the target user across internal IDP, requestor-derived credentials, LDAP DN lookup, and OIDC/LDAP claims before calling `globalIAMSys.NewServiceAccount`. Updates require `policy.UpdateServiceAccountAdminAction`; self-update is intentionally not allowed pending redesign. Info/list/delete allow a narrower self-service path by comparing the caller's parent user with the service account parent when the caller lacks broad list/remove permissions.

Access-key listing (`ListAccessKeysBulk`) supports all-users, explicit users, and self-only modes. All-users requires list-users permission, and access-key listing requires list-service-accounts permission with deny-only behavior for self mode. It can list STS keys, service accounts, both, or neither based on `listType`, and encrypts the response with the caller secret.

Policy flows validate policy names, content length, JSON policy syntax, non-empty policy version, LDAP DN normalization for LDAP mappings, and root/temporary-user restrictions for legacy mappings. Modern attach/detach requires octet-stream encrypted request bodies, validates `madmin.PolicyAssociationReq`, calls `PolicyDBUpdateBuiltin`, returns encrypted attached/detached results, and records policy names in audit context.

`AccountInfoHandler` computes account-level console data: bucket access by checking list/location and put permissions, bucket usage/quota/object-lock/replication/tagging details, backend info, and effective policy. Effective policy comes from consoleAdmin for root or external authZ plugin, role policy for OpenID role ARN, policies embedded in OpenID claims, or IAM policy DB for internal/LDAP users and groups.

`ExportIAM` streams a zip response containing policies, internal users, groups, service accounts, and policy mappings. It reads lower-level IAM store data directly, skips the site-replicator service account, includes service-account claims/session policies/metadata, and uses deflated zip entries under `iam-assets`. `importIAM` reads the zip into memory, opens each known asset if present, imports policies first, then users, groups, service accounts, user mappings, group mappings, and STS-user mappings. It supports LDAP normalization/skipping for service accounts and mappings, deletes an existing service account before clean re-import, accumulates `added`, `removed`, `skipped`, and `failed` entities, and returns a structured `madmin.ImportIAMResult` only for v2.

## State And Persistence Behavior
The file is state-heavy. It mutates IAM users, service accounts, temporary-account token state, groups, policies, and policy mappings through `globalIAMSys`. Some read paths use high-level IAM APIs, while export/import reaches into `globalIAMSys.store` to load users, groups, and mapped policies. IAM state may be backed by local object storage/config or etcd depending on deployment.

Site replication is a cross-cutting persistence integration. User, group, policy, policy-mapping, and non-root service-account changes call `globalSiteReplicationSys.IAMChangeHook` with `madmin.SRIAMItem` payloads and timestamps so peer clusters can converge. Root-owned service accounts are deliberately not replicated in several paths. The site-replicator service account is protected from deletion while site replication is enabled and omitted from export.

Encryption is part of the admin API state contract. Many madmin requests and responses use `madmin.EncryptData`/`DecryptData` with the requestor's secret key, while some older policy endpoints return plain JSON. Content-length and maximum-size checks protect encrypted config bodies and policy bodies in several endpoints.

Derived credentials are handled carefully. The code distinguishes `cred.AccessKey`, `cred.ParentUser`, groups, claims, service-account status, STS status, OpenID role/policy claims, LDAP normalized DNs, and root credentials. Authorization state often uses parent-user policy for derived credentials while still recording the derived access key for request context.

## Dependencies And Integration Points
The file depends on `madmin-go/v3`, MinIO internal `auth`, DNS/bucket federation config, logger request info, mux route variables, LDAP helpers, policy parsing/evaluation, zip compression, `xsync` mapped-policy maps, global IAM/site-replication/bucket metadata systems, admin error mapping, and shared helper functions for condition values and provider inference.

It integrates with `admin-handlers-site-replication.go` through `madmin.SRIAMItem` payloads, with `admin-handlers-idp-openid.go` through shared access-key and OpenID claim conventions, with S3 authorization through policy evaluation, and with admin clients in `madmin-go` through encrypted request/response types.

## Risks And Test Signals
This file has a large security surface. High-risk areas include self-service denial semantics, service-account policy escalation, target-user confusion for derived credentials, LDAP DN normalization, OpenID claim-policy handling, root-account protections, import overwrites, and site-replication hook omissions. The code contains explicit regression protections against regular users escalating via `AddUser`, service accounts updating their own policy, and restricted service accounts creating broader service accounts.

Operational risks include whole-body reads for IAM import, partial import behavior that can add some entities before failing later, direct store access during export/import, and differences between local IAM and etcd-backed IAM. `ImportIAMV2` improves observability by returning added/removed/skipped/failed entities, but non-v2 import has no structured success body.

The companion tests in this work item provide strong signals for internal IDP user lifecycle, policy create/delete/validation, default policies, group membership/status effects, service-account creation/list/info/session-policy/secret/status/delete behavior, `svc:DurationSeconds` conditions, access-management-plugin behavior, user policy escalation regression, and two service-account privilege escalation regressions. The race test adds a concurrent deletion/invalidation signal. Missing direct signals in this subset include OpenID access-key listing, IAM import/export, token revocation, LDAP-specific attach/detach/import normalization, and site-replication hook delivery.

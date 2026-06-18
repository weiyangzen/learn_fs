# sources/object-store/minio/cmd/admin-handlers-idp-openid.go

## Purpose
`admin-handlers-idp-openid.go` implements the OpenID-specific bulk access-key listing admin endpoint: `GET /minio/admin/v3/idp/openid/list-access-keys-bulk`. It complements the generic IAM access-key bulk listing handler by grouping STS and service-account credentials by OpenID configuration and OpenID parent identity rather than by internal MinIO user alone.

## Important APIs, Types, And Functions
The file defines `dummyRoleARN`, used as a synthetic role ARN bucket for claim-policy OpenID providers that do not set an explicit role ARN. The only handler, `adminAPIHandlers.ListAccessKeysOpenIDBulk`, returns encrypted JSON containing `[]madmin.ListAccessKeysOpenIDResp`.

The handler uses `validateAdminSignature` instead of the simpler `validateAdminReq` because it needs both the authenticated credentials and an owner flag, then performs fine-grained `globalIAMSys.IsAllowed` checks. It consumes query/form parameters `users`, `all`, `configName`, `allConfigs`, and `listType`, and it interprets `madmin.AccessKeyListUsersOnly`, `AccessKeyListSTSOnly`, `AccessKeyListSvcaccOnly`, and `AccessKeyListAll`.

The IAM/OpenID integration points are `globalIAMSys.OpenIDConfig.Enabled`, `GetConfigList`, `GetUserIDClaim`, and `GetUserReadableClaim`; credential enumeration comes from `globalIAMSys.ListAllAccessKeys`. Responses use `madmin.OpenIDUserAccessKeys`, `madmin.ServiceAccountInfo`, and `madmin.EncryptData`.

## Control Flow
The handler first rejects uninitialized object/notification layers, invalid signatures, and disabled OpenID configuration. It derives request mode: all users, specific user list, or self-only. `all=true` requires `policy.ListUsersAdminAction`; listing access keys requires `policy.ListServiceAccountsAdminAction`, with `DenyOnly` set for self-only requests so explicit denies still block self-service reads.

It normalizes OpenID config selection: if neither `configName` nor `allConfigs` is provided, it defaults to `madmin.Default`; `all=true` cannot be combined with explicit `users`. It then builds a role-ARN-to-config map from the active OpenID provider configuration list. Configs without role ARNs are mapped under `dummyRoleARN` for claim-based providers. If no target config matches, it returns `ErrAdminNoSuchConfigTarget`.

The access-key scan filters every credential from `ListAllAccessKeys`: it requires a `sub` claim, applies `listType` to distinguish STS versus service accounts, matches role ARN or OpenID policy claim to the requested provider config, optionally matches requested users by parent user or provider ID claim, then accumulates each key under its OpenID config and parent MinIO access key. Finally it sorts users inside each config and sorts configs by name before encrypting the response with the caller's secret key.

## State And Persistence Behavior
This handler is read-only. It does not mutate IAM state, OpenID state, or site-replication state. Its observable state is a point-in-time traversal of persisted or cached IAM credentials and server OpenID provider configuration. It intentionally exposes only access key names and expirations, not secret keys. Response confidentiality depends on `madmin.EncryptData(cred.SecretKey, data)` matching the admin client protocol.

The most important state distinction is between OpenID STS keys and OpenID-created service accounts. The handler classifies an access key by `accessKey.IsServiceAccount()` after confirming OpenID claims. It also treats OpenID credentials without a `roleArn` claim but with the OpenID IAM policy claim as belonging to the synthetic config role bucket.

## Dependencies And Integration Points
The file depends on `madmin-go/v3` response and list-type constants, MinIO's string-set helper, MinIO policy action constants, global IAM and server config state, admin signature validation, and shared JSON error helpers. It integrates with the generic access-key listing behavior in `admin-handlers-users.go` but differs by using OpenID provider config metadata and OpenID claims to group results.

## Risks And Test Signals
Security risk concentrates around user filtering and self-service permissions. The handler must not allow a user to infer other users' OpenID access keys without `ListUsersAdminAction` and `ListServiceAccountsAdminAction`. The `DenyOnly` path for self-only access is a notable safeguard and should be preserved if this code is refactored.

Correctness risk exists around providers without role ARN, mixed multiple OpenID configs, and custom ID/readable claims. `dummyRoleARN` can group all claim-based providers together if multiple configs are claim-based; the surrounding config map stores the dummy ARN once, so multi-config claim-policy setups require care. There are no direct tests in this work item for this file; indirect signals come from OpenID/IAM admin tests elsewhere and from generic access-key listing semantics in `admin-handlers-users.go`.

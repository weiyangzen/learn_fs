# sources/object-store/rustfs/crates/madmin/src/user.rs

Purpose: models admin IAM users, access keys, service accounts, account access summaries, site-replication service-account exports, and IAM import/entity results.

Important APIs/types/functions: `AccountStatus` serializes enabled/disabled and implements `AsRef<str>`/`TryFrom<&str>`. `UserAuthType`, `UserAuthInfo`, `UserInfo`, and `AddOrUpdateUserReq` cover users. `ServiceAccountInfo`, list responses, `AddServiceAccountReq`, `UpdateServiceAccountReq`, `Credentials`, `AddServiceAccountResp`, `InfoServiceAccountResp`, `InfoAccessKeyResp`, LDAP/OpenID-specific info, and access-key list constants cover service-account APIs. Validation helpers enforce name, description, and expiration rules. `SRSessionPolicy` preserves raw JSON/null for replication. `SRSvcAccCreate` and IAM import/entity structs support site replication/import reporting.

Control flow: request `validate` methods delegate to helpers: names may be empty but, if set, must be <=32 chars, ASCII alphanumeric/underscore/hyphen, and start with a letter; descriptions are <=256 bytes; expiration must be future unless unix timestamp zero. Policy values are normalized so JSON strings become JSON objects when parseable. Service-account expiration deserialization accepts RFC3339 and a legacy exported format, trims empty strings, and maps zero timestamp to `None`.

State and persistence: no storage. The module represents persisted IAM state and import/export payloads, including raw session policy JSON to avoid lossy replication.

Dependencies/integration: uses serde, `serde_json::Value`/`RawValue`, `time`, and `BackendInfo`. `site_replication.rs` imports `SRSvcAccCreate` and `UserInfo`; `lib.rs` re-exports this module.

Risks: several structs serialize credentials/secrets. Validation uses byte length for descriptions but char iteration for names; expiration validation depends on current UTC time. Raw policy equality is textual, so semantically equivalent JSON with different formatting may compare unequal.

Test signals: broad unit tests cover account status conversion/serde, user/service-account construction, validation success/failure, generated credentials, stringified policy JSON, missing policies, credential serialization, access/account summaries, round trips, debug/memory checks, edge cases, empty/legacy/RFC3339 service-account expiration handling.

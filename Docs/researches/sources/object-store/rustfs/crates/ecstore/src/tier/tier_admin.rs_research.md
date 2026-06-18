# sources/object-store/rustfs/crates/ecstore/src/tier/tier_admin.rs

## Purpose

Defines the admin credential payload used for editing tier credentials.

## Important APIs and Types

`TierCreds` is a serde DTO with access/secret keys, AWS role fields, web identity token file/ARN, and `creds_json`.

## Control Flow

No functions. `TierConfigMgr::edit` consumes this DTO and applies fields per provider.

## State and Persistence Behavior

Transient request state only; persistence occurs when the tier manager saves updated configs.

## Dependencies and Integration Points

Depends on serde and integrates with admin tier edit paths.

## Risks and Edge Cases

`creds_json` has no active serde rename. Partial credentials are possible and validated later by manager/provider logic.

## Test Signals

No direct tests; admin API serialization and credential update tests should cover it.

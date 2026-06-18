
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/validation/ValidationCondition.java

Purpose: Enumerates runtime conditions under which request validators should apply.

Important APIs and types: Enum values `CLUSTER_NEEDS_FINALIZATION` and `OLDER_CLIENT_REQUESTS`; abstract method `shouldApply(OMRequest, ValidationContext)`.

Control flow: `CLUSTER_NEEDS_FINALIZATION` checks `ctx.versionManager().needsFinalization()`. `OLDER_CLIENT_REQUESTS` compares request version with `ClientVersion.CURRENT_VERSION`.

State and persistence behavior: No persisted state. Reads request version and layout-version-manager state.

Dependencies and integration points: Used by `RequestValidations.conditions` and validator registry selection to activate compatibility validators.

Risks: Null context will break finalization checks. The older-client check assumes integer version ordering remains monotonic. Tests should cover finalized/pre-finalized contexts and old/current/future request versions.

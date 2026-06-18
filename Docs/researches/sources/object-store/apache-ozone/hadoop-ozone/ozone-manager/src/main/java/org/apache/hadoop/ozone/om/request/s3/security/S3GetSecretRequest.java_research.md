## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/security/S3GetSecretRequest.java

Purpose: `S3GetSecretRequest` returns an S3 secret for an access ID and, by default, creates one if it does not exist. In HA mode it transforms a client get request into a replicated request that includes the generated secret.

Important APIs/types/functions: `preExecute` reads `GetS3SecretRequest.kerberosID` as access ID, checks permission with `S3SecretRequestHelper`, normalizes `createIfNotExist`, generates a SHA-256 secret from `OmUtils.getSHADigest` when needed, and attaches `UpdateGetS3SecretRequest`. `validateAndUpdateCache` uses `S3SecretManager.doUnderLock`, `getSecret`, `updateCache`, optional `storeSecret` for non-batch stores, `OMMultiTenantManager`, and `S3GetSecretResponse`.

Control flow: PreExecute checks permission and builds a new OM request. If create-if-not-exist is true, it embeds the generated AWS secret into `UpdateGetS3SecretRequest` for Ratis replication. Validate/update locks the access ID, reads existing secret state, creates and caches a new secret if absent and allowed, returns no secret with `ACCESS_ID_NOT_FOUND` if absent and creation is false, rejects non-tenant legacy duplicate secrets with `S3_SECRET_ALREADY_EXISTS`, and returns existing tenant secrets for assigned tenant access IDs.

State and persistence behavior: New secrets are staged in the secret manager cache with the transaction index. For stores without batch support, `storeSecret` is called immediately inside the lock so third-party storage failures can fail the request. Existing secrets are not overwritten by get. The response carries a nullable assigned value plus manager for replay.

Dependencies and integration points: It integrates secret generation, HA replication, tenant manager access-ID ownership, secret manager locking/storage, audit under `OMAction.GET_S3_SECRET`, and compatibility with the protobuf field still named `kerberosID`.

Risks and edge cases: Secret generation must happen before Ratis replication so followers persist the same value. Existing non-tenant secrets trigger `S3_SECRET_ALREADY_EXISTS`, while tenant access IDs return existing secrets; this distinction is subtle. `createIfNotExist` defaults to true when omitted. The code asserts the recomposed request has the field set.

Test signals: Cover create default behavior, createIfNotExist=false missing access ID, existing tenant secret return, existing non-tenant duplicate rejection, HA replicated generated secret consistency, non-batch store failure, permission checks, audit fields, and response secret contents.

# sources/object-store/minio-mc/cmd/idp-ldap-accesskey-enable.go

Purpose: Implements enabling and shared enable/disable status changes for LDAP access keys.

Important APIs/types/functions: `idpLdapAccesskeyEnableCmd`, `mainIDPLdapAccesskeyEnable`, and `enableDisableAccesskey`.

Control flow: The helper accepts target and access key, initializes admin client, chooses operation/status (`on` for enable, `off` for disable), calls `UpdateServiceAccount` with `NewStatus`, and prints success.

State and persistence: Mutates remote service-account status.

Dependencies/integration: Used by both enable and disable command files. Depends on `newAdminClient`, `madmin.UpdateServiceAccountReq`, and `accesskeyMessage`.

Risks: Syntax check allows a single arg and leaves access key empty. Fatal message says "Unable to add service account" during status update, which is misleading.

Test signals: No direct tests.

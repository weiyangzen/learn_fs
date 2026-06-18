# Research: sources/object-store/minio-mc/cmd/idp-openid-accesskey-enable.go

Purpose: implements `mc idp openid accesskey enable`.

Important APIs/types/functions: `idpOpenidAccesskeyEnableCmd` and `mainIDPOpenIDAccesskeyEnable`, delegating to `enableDisableAccesskey(ctx, true)`.

Control flow: wrapper registers the command, then the shared helper validates target/access key and updates status on the server.

State and persistence: enables an access key server-side.

Dependencies/integration points: shared access-key enable/disable helper and MinIO admin API.

Risks: help example says LDAP; actual behavior is OpenID namespace but backend operation is provider-neutral.

Test signals: no direct tests; command-level test should assert `enable=true` delegation and output message.

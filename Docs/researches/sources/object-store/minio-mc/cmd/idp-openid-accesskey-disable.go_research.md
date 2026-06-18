# Research: sources/object-store/minio-mc/cmd/idp-openid-accesskey-disable.go

Purpose: implements `mc idp openid accesskey disable`.

Important APIs/types/functions: `idpOpenidAccesskeyDisableCmd` and `mainIDPOpenIDAccesskeyDisable`, which delegates to shared `enableDisableAccesskey(ctx, false)`.

Control flow: CLI validation and actual server mutation happen in the shared helper from LDAP access-key enable/disable code. This wrapper supplies OpenID command metadata and help.

State and persistence: disables a service account/access key server-side through shared admin APIs.

Dependencies/integration points: depends on global command setup and shared access-key enable/disable implementation.

Risks: help examples say LDAP even though this is OpenID, which can confuse users. Behavior is shared with LDAP and not OpenID-specific.

Test signals: no direct tests; should verify command path delegates with `enable=false`.

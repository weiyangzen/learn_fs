# Research: sources/object-store/minio-mc/cmd/idp-ldap-accesskey-sts-revoke.go

Purpose: implements `mc idp ldap accesskey sts-revoke`, revoking STS tokens for an LDAP user or for the authenticated LDAP service account.

Important APIs/types/functions: `idpLdapAccesskeySTSRevokeCmd` and `mainIdpLdapAccesskeySTSRevoke`. It reuses `adminAccesskeySTSRevokeFlags`, `checkSTSRevokeSyntax`, and `stsRevokeMessage` from admin access-key code, then calls `madmin.AdminClient.RevokeTokens`.

Control flow: validates syntax, extracts alias, optional user, `--token-type`, and `--all`, creates an admin client, sends `madmin.RevokeTokensReq`, and prints token-revoke output.

State and persistence: mutates server-side STS token state by invalidating matching tokens. No local persistence.

Dependencies/integration points: tied to shared admin access-key revoke validation and message types; operates through MinIO admin API.

Risks: broad `--all` revocation is destructive for active sessions. Empty user is meaningful for `--self`, so validation in the shared helper is critical.

Test signals: no local tests; should cover `--all` versus `--token-type`, `--self`, non-self user, and request payload shape.

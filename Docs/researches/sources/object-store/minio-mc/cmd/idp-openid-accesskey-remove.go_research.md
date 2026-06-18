# Research: sources/object-store/minio-mc/cmd/idp-openid-accesskey-remove.go

Purpose: implements `mc idp openid accesskey remove`/`rm`.

Important APIs/types/functions: `idpOpenidAccesskeyRemoveCmd` and `mainIDPOpenIDAccesskeyRemove`, delegating to `commonAccesskeyRemove`.

Control flow: wrapper registers help and command metadata. Shared helper validates target plus access key, creates admin client, deletes the service account, and prints success.

State and persistence: deletes a server-side service account access key.

Dependencies/integration points: same backend as LDAP access-key remove through `DeleteServiceAccount`.

Risks: provider-neutral deletion means the command path does not itself verify OpenID ownership; server authorization and access-key identity decide outcome.

Test signals: no direct tests; shared remove behavior should be tested once and command wiring smoke-tested.

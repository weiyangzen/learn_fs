# Research: sources/object-store/minio-mc/cmd/idp-openid-accesskey-info.go

Purpose: implements `mc idp openid accesskey info`, showing OpenID identity metadata for access keys.

Important APIs/types/functions: `idpOpenidAccesskeyInfoCmd`, `openIDAccessKeyInfo`, `openIDAccessKeyInfo.String`, and `mainIDPOpenIDAccesskeyInfo`.

Control flow: command requires target and one or more access keys, then delegates lookup to `commonAccesskeyInfo`. The display type renders config name, display-name claim/value when present, and user ID claim/value; default config `_` is shown as `_ (default)`.

State and persistence: read-only against server-side access-key metadata.

Dependencies/integration points: depends on shared info helper and `iFmt` from LDAP policy formatting.

Risks: OpenID output differs from LDAP info shape, so shared helper must select the right message type. Claim labels come from server data and should be treated as display text.

Test signals: no direct tests; should cover default config formatting, missing display-name claim, and JSON output.

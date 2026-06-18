# Research: sources/object-store/minio-mc/cmd/idp-openid-accesskey-list.go

Purpose: implements `mc idp openid accesskey list`/`ls`, listing OpenID users and their STS/service-account access keys.

Important APIs/types/functions: `idpOpenIDAccesskeyListFlags`, `openIDAccesskeyList`, and `mainIDPOpenIDAccesskeyList`. It reuses `commonAccesskeyList` and calls `ListAccessKeysOpenIDBulk`.

Control flow: common parsing supports target config names and `--all-configs`. The command calls the OpenID bulk listing API, retries Access Denied tentative-all as self, then prints one message per OpenID config. The string renderer shows config name, MinIO access key, external ID, readable name, and keys with humanized expiry and STS marker.

State and persistence: read-only server query.

Dependencies/integration points: madmin OpenID access-key list types, humanize time formatting, lipgloss, colorjson, and shared access-key parser.

Risks: shares LDAP-oriented flag names such as `users-only` and common error strings; exact Access Denied string matching is brittle. Output contains relative expiry text in console mode, so scripts should use JSON.

Test signals: no direct tests; should cover all-configs, config suffix parsing, list filters, and mixed STS/service accounts.

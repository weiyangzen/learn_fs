# Research: sources/object-store/minio-mc/cmd/idp-openid-accesskey-edit.go

Purpose: implements `mc idp openid accesskey edit`.

Important APIs/types/functions: `idpOpenIDAccesskeyEditFlags`, `idpOpenidAccesskeyEditCmd`, and `mainIDPOpenIDAccesskeyEdit`, delegating to `commonAccesskeyEdit`.

Control flow: this file declares editable attributes: secret key, policy file, friendly name, description, expiry duration, and absolute expiry. The shared helper validates args, builds `madmin.UpdateServiceAccountReq`, and calls the admin API.

State and persistence: mutates server-side service-account metadata and credentials.

Dependencies/integration points: shared with LDAP edit. It relies on policy-file reading and expiry parsing in the common helper.

Risks: secret-key changes are sensitive and may break clients. Help uses generic `[TARGET]` wording, so shared helper validation must remain authoritative.

Test signals: no direct tests; exercise each flag and mutual expiry handling in shared helper tests.

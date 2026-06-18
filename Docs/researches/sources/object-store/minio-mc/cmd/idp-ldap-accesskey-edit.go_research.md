# sources/object-store/minio-mc/cmd/idp-ldap-accesskey-edit.go

Purpose: Implements editing properties of existing LDAP access keys/service accounts.

Important APIs/types/functions: `idpLdapAccesskeyEditFlags`, `idpLdapAccesskeyEditCmd`, `mainIDPLdapAccesskeyEdit`, `commonAccesskeyEdit`, and `accessKeyEditOpts`.

Control flow: Requires target and access key, builds update options, initializes admin client, calls `UpdateServiceAccount`, and prints success. Option parsing requires at least one editable property, rejects both expiry forms together, validates optional non-empty policy file, and parses absolute or duration expiry.

State and persistence: Reads optional policy file and mutates remote service-account metadata/secret/policy/expiration.

Dependencies/integration: Uses `madmin.UpdateServiceAccountReq`, policy parser, supported time formats, and shared output message.

Risks: Argument check allows one arg even though `accessKey` is then empty, likely causing server-side failure instead of local syntax help. Example contains `---expiry-duration` typo.

Test signals: No direct tests.

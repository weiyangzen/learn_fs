# sources/object-store/minio-mc/cmd/idp-ldap-accesskey-info.go

Purpose: Registers LDAP access-key info command and LDAP-specific string rendering for username.

Important APIs/types/functions: `idpLdapAccesskeyInfoCmd`, `ldapAccessKeyInfo`, `String`, and `mainIDPLdapAccesskeyInfo`.

Control flow: The command delegates to shared `commonAccesskeyInfo`. `ldapAccessKeyInfo.String` renders a green "Username:" label and username via lipgloss.

State and persistence: Read-only remote info through shared helper; no local persistence here.

Dependencies/integration: Uses global flags, shared access-key info implementation, and lipgloss for human output.

Risks: Most behavior is outside this file. Output styling is separate from JSON behavior defined elsewhere.

Test signals: No direct tests.

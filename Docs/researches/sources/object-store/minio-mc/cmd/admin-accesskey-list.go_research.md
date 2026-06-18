<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-accesskey-list.go -->
# sources/object-store/minio-mc/cmd/admin-accesskey-list.go

## Purpose
Implements `mc admin accesskey list/ls`, listing users and their STS/service-account access keys with filters for self, all, temporary-only, service-account-only, and users-only views.

## Important APIs, types, and functions
Defines list flags, `adminAccesskeyListCmd`, `userAccesskeyList` with `String`/`JSON`, and `mainAdminAccesskeyList`.

## Control flow
Shared `commonAccesskeyList` parses alias/users/options. The command calls `ListAccessKeysBulk`; if an unauthenticated all-users probe gets Access Denied under tentative-all mode, it retries without `All`. Results are printed per user.

## State and persistence behavior
Read-only against server IAM state. No local files are written.

## Dependencies and integration points
Depends on madmin `ServiceAccountInfo`, shared access-key listing parser, colorjson, lipgloss, humanized expiration, and global output mode.

## Risks and test signals
String comparison on `Access Denied.` is brittle. Tests should cover self/all fallback, LDAP label mode, empty users, filter combinations, and JSON output.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-accesskey-list.go -->

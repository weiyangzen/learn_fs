<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-accesskey-info.go -->
# sources/object-store/minio-mc/cmd/admin-accesskey-info.go

## Purpose
Implements `mc admin accesskey info`, retrieving and formatting metadata for one or more access keys including parent user, policy source, status, expiration, STS flag, and identity-provider details.

## Important APIs, types, and functions
Defines `adminAccesskeyInfoCmd`, `accesskeyMessage` with `String`/`JSON`, `providerInfo`, `mainAdminAccesskeyInfo`, `commonAccesskeyInfo`, and `nilExpiry`.

## Control flow
The command requires target plus at least one access key, creates an admin client, calls `InfoAccessKey` for each key, maps LDAP/OpenID provider-specific fields into display structs, and prints each message.

## State and persistence behavior
No local persistence. It reads server IAM/access-key state and emits text or JSON.

## Dependencies and integration points
Uses madmin access-key APIs, colorjson, lipgloss styling, humanized expiration times, shared CLI/probe/error helpers, and provider-specific message types defined elsewhere.

## Risks and test signals
Provider-specific nil fields and sentinel expiration handling are edge cases. Tests should cover multiple keys, LDAP/OpenID/builtin providers, JSON redaction/omitempty behavior, and disabled status rendering.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-accesskey-info.go -->

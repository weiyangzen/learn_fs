<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-accesskey-sts-revoke.go -->
# sources/object-store/minio-mc/cmd/admin-accesskey-sts-revoke.go

## Purpose
Implements `mc admin accesskey sts-revoke`, revoking all STS tokens or a specific token type for a named user or the authenticated user.

## Important APIs, types, and functions
Defines flags `--all`, `--self`, and `--token-type`, `adminAccesskeySTSRevokeCmd`, `stsRevokeMessage`, `checkSTSRevokeSyntax`, and `mainAdminAccesskeySTSRevoke`.

## Control flow
Syntax validation enforces target presence, user-vs-self exclusivity, and exactly one revoke mode. The handler creates an admin client, calls `RevokeTokens` with `madmin.RevokeTokensReq`, and prints a success message.

## State and persistence behavior
No local persistence. It mutates server-side STS/token state through the admin API.

## Dependencies and integration points
Depends on madmin token revoke API, shared CLI/probe/fatal handling, and MinIO output formatting.

## Risks and test signals
Argument exclusivity is critical to avoid revoking wrong tokens. Tests should cover all invalid flag combinations, self mode, named user mode, token-type mode, and API error propagation.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-accesskey-sts-revoke.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_util_token.h -->
# sources/user-network-fs/samba/source3/registry/reg_util_token.h

Purpose: Public header for the registry admin-token helper.

Important APIs, types, and functions: Declares `registry_create_admin_token(TALLOC_CTX *mem_ctx, struct security_token **ptoken)`.

Control flow: No executable logic. The single API returns an `NTSTATUS` and publishes a talloc-owned `security_token`.

State and persistence behavior: No header-owned state. Output token lifetime is controlled by the caller's talloc context.

Dependencies and integration points: Included by registry management code that needs a local administrative token for registry access checks.

Risks: The prototype does not describe that the token is synthetic and privileged; misuse outside tightly scoped local registry access would bypass normal caller identity semantics.

Test signals: Compile coverage for token consumers and behavioral tests in `reg_util_token.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/registry/reg_util_token.h -->

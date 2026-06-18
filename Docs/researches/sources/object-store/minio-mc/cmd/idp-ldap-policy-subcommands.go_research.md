# Research: sources/object-store/minio-mc/cmd/idp-ldap-policy-subcommands.go

Purpose: implements LDAP policy association commands: attach, detach, and entities.

Important APIs/types/functions: `mainIDPLdapPolicyAttach`, `mainIDPLdapPolicyDetach`, `mainIDPLdapPolicyEntities`, `policyAssociationMessage`, `policyEntities`, `iFmt`, and `builderWrapper`. Admin calls are `AttachPolicyLDAP`, `DetachPolicyLDAP`, and `GetLDAPPolicyEntities`.

Control flow: attach requires target plus at least one policy and constructs `madmin.PolicyAssociationReq`, relying on `req.IsValid()` to enforce exactly one entity. Detach performs its own missing-entity check and calls server detach. Entities accepts repeated `--user`, `--group`, and `--policy` filters, fetches mappings, and renders user, group, policy, group membership, and effective-policy sections.

State and persistence: attach/detach mutate server-side LDAP policy mappings. Entities is read-only.

Dependencies/integration points: integrates with `madmin.PolicyEntitiesResult`, `lipgloss`, `colorjson`, and MinIO set utilities for effective-policy calculation.

Risks: detach does not call `PolicyAssociationReq.IsValid`, so multiple entity flags may reach the server depending on server validation. Text wrapping is display-only and must not be treated as a parseable API.

Test signals: no direct tests; useful coverage includes attach/detach validation, entities formatting with group membership, and JSON output.

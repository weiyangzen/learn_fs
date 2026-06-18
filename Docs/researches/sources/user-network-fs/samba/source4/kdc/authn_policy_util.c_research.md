# sources/user-network-fs/samba/source4/kdc/authn_policy_util.c

## Purpose

`authn_policy_util.c` implements Samba KDC helpers for Active Directory authentication silos and authentication policies. It discovers policies assigned directly or through silos, extracts Kerberos/NTLM/server restriction data, performs security descriptor access checks for authentication restrictions, and creates audit-info structures describing allowed or denied decisions.

## Important APIs, Types, and Functions

Feature gates are `authn_policy_silos_and_policies_in_effect()` for FL2012_R2 and `authn_policy_allowed_ntlm_network_auth_in_effect()` for FL2016. Discovery helpers include `authn_policy_get_attrs()`, `authn_policy_get_assigned_silo()`, and `samba_kdc_authn_policy_msg()`. Public policy lookup functions are `authn_policy_kerberos_client()`, `authn_policy_ntlm_client()`, and `authn_policy_server()`. Enforcement functions are `authn_policy_authenticate_from_device()`, `authn_policy_ntlm_apply_device_restriction()`, and `authn_policy_authenticate_to_service()`. Audit helpers include `_authn_policy_audit_info()` and typed wrappers for Kerberos client, NTLM client, and server policies.

## Control Flow

Policy lookup starts by classifying the account as user, computer, or managed service account and selecting the relevant silo/policy attribute names. `authn_policy_get_assigned_silo()` verifies `msDS-AssignedAuthNPolicySilo`, confirms the account DN appears in `msDS-AuthNPolicySiloMembers`, and reports whether the silo is enforced. `samba_kdc_authn_policy_msg()` chooses the policy from the silo or direct `msDS-AssignedAuthNPolicy`, reads the policy object, and records policy/silo names and enforcement state. Typed lookup functions then copy relevant descriptor blobs, NTLM booleans, or TGT lifetime values into policy structs.

## State and Persistence Behavior

The implementation reads DSDB policy/silo objects and does not modify directory state. It creates talloc-owned policy and audit structures for callers. Descriptor blobs are stolen from searched LDB messages into policy objects so their data survives temporary context cleanup. Audit info stores references to client info and copies policy names/status so later logging can happen after enforcement code frees temporary objects.

## Dependencies and Integration Points

The file depends on `auth/authn_policy_impl.h`, generated auth policy types, DSDB search helpers, loadparm, security descriptor NDR parsing, `auth_generate_security_token()`, claims-aware security token construction, and `sec_access_check_ds()`. It integrates with Kerberos device restrictions, NTLM network authentication policy, and server-side authentication-to-service checks.

## Risks and Edge Cases

Functional-level gates intentionally ignore policies below FL2012_R2 and the NTLM network-auth boolean below FL2016. Missing objectClass or unsupported account classes produce no policy rather than hard failure. Access-check enforcement depends on valid security descriptors with owners; invalid descriptors return audit reasons and can deny when enforced. If a policy is not enforced, access-check failures are converted back to success after audit info is produced.

## Test Signals

Good coverage includes direct policy vs silo policy precedence, enforced vs audit-only behavior, user/computer/service account attribute selection, missing/deleted silo or policy objects, descriptor parse failures, ownerless descriptors, device compound-authentication flags, NTLM denial when device restrictions exist and allowed NTLM is false, and server restriction checks for both Kerberos and NTLM audit event types.

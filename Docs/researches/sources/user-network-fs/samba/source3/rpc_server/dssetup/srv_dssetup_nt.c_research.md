# sources/user-network-fs/samba/source3/rpc_server/dssetup/srv_dssetup_nt.c

Purpose: implements the DSSETUP RPC server surface needed to report primary domain role information, with the rest of the domain-controller promotion/demotion operations explicitly unsupported.

Important APIs/types/functions: `fill_dsrole_dominfo_basic` and `_dssetup_DsRoleGetPrimaryDomainInformation` are the implemented path. All other `_dssetup_DsRole*` entry points set `p->fault_state = DCERPC_FAULT_OP_RNG_ERROR` and return `WERR_NOT_SUPPORTED`.

Control flow: `fill_dsrole_dominfo_basic` allocates a `dssetup_DsRolePrimaryDomInfoBasic`, maps `lp_server_role()` to standalone/member/backup-DC/primary-DC role values, fills the NetBIOS domain name from Samba global state, optionally adds the stored domain GUID, and, for ADS security, lowercases `lp_realm()` into DNS domain and forest fields. `_dssetup_DsRoleGetPrimaryDomainInformation` dispatches level `DS_ROLE_BASIC_INFORMATION` to that helper and rejects unknown levels with `WERR_INVALID_LEVEL`.

State/persistence behavior: no state is modified. It reads live Samba configuration, secrets.tdb domain GUID data via `secrets_fetch_domain_guid`, and realm/workgroup/server-role settings.

Dependencies/integration: tied to loadparm role/security configuration, Samba secrets, generated `ndr_dssetup` server compatibility code, and standard RPC pipe memory contexts.

Risks/test signals: role mapping must stay aligned with Samba server-role semantics, especially IPA DC being reported as primary DC. ADS DNS fields depend on lowercase conversion. Tests should cover each server role, ADS versus domain security, missing domain GUID, invalid info levels, and unsupported calls generating the expected DCERPC fault.

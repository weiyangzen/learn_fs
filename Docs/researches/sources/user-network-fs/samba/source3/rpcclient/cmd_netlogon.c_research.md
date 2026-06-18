# sources/user-network-fs/samba/source3/rpcclient/cmd_netlogon.c

## Purpose
`cmd_netlogon.c` implements the `rpcclient` NETLOGON command set. It provides commands for domain controller discovery, logon-control operations, secure-channel logon/password operations, trust enumeration, DNS deregistration, forest trust queries, site coverage, capabilities probing, and `LogonGetDomainInfo`.

## Important APIs, types, and functions
- DC discovery commands wrap `netr_GetAnyDCName`, `netr_GetDcName`, `netr_DsRGetDCName`, `netr_DsRGetDCNameEx`, and `netr_DsRGetDCNameEx2`.
- Logon-control commands use `dcerpc_netr_LogonControl()` and `dcerpc_netr_LogonControl2()` with `union netr_CONTROL_*` request/response structures.
- Secure-channel commands include `cmd_netlogon_sam_logon()`, `cmd_netlogon_change_trust_pw()`, `cmd_netlogon_capabilities()`, and `cmd_netlogon_logongetdomaininfo()`.
- Trust/site commands call `LogonGetTrustRid`, `DsrEnumerateDomainTrusts`, `DsrDeregisterDNSHostRecords`, `DsRGetForestTrustInformation`, `NetrEnumerateTrustedDomains`, `NetrEnumerateTrustedDomainsEx`, and `DsrGetDcSiteCoverageW`.
- Secure-channel state is supplied through globals declared elsewhere: `rpcclient_netlogon_creds` and `rpcclient_msg_ctx`.
- The exported `netlogon_commands[]` table marks commands that require secure-channel credentials with `.use_netlogon_creds = true`.

## Control flow
Most commands parse optional server/domain/site/GUID/flag parameters, call one generated NETLOGON RPC through `cli->binding_handle`, translate transport `NTSTATUS` into `WERROR` for WERROR commands, then print the useful output. The older `getanydcname` and `getdcname` commands temporarily raise the RPC timeout to at least thirty seconds so the target DC has time to answer. DS discovery commands print the NDR-rendered `netr_DsRGetDCNameInfo` structure on success.

Secure-channel commands use higher-level helpers. `samlogon` requires `rpcclient_netlogon_creds`, generates a random logon ID, calls `rpccli_netlogon_password_logon()`, and maps the returned validation union to `netr_SamInfo3`. `change_trust_pw` forces a trust-password update with `trust_pw_change()`. `capabilities` takes an exclusive netlogon credentials lock, checks the secure channel, and prints server capabilities. `logongetdomaininfo` sends an empty `netr_WorkstationInformation` query through `netlogon_creds_cli_LogonGetDomainInfo()`.

## State and persistence behavior
Most commands are read-only discovery/control calls and persist no local state. `change_trust_pw` mutates the machine/trust account password on the remote domain controller and local secrets through the helper stack. `deregisterdnsrecords` mutates remote DNS registration state. Secure-channel commands consume and may update netlogon credential state maintained outside this file. Temporary timeout changes are restored before the command returns.

## Dependencies and integration points
The module depends on generated `ndr_netlogon` stubs, `rpc_client/cli_netlogon.h`, `rpc_client/util_netlogon.h`, `netlogon_creds_cli`, `secrets.h`, loadparm (`lp_workgroup()`), GUID parsing, NDR pretty-printing, and rpcclient command registration. It integrates with rpcclient's secure-channel setup through the `.use_netlogon_creds` flag and global credential handles.

## Risks and edge cases
- `samlogon` takes a plaintext password argument, so command history and process listings can expose credentials.
- `change_trust_pw` is a destructive administrative operation because it forcibly rotates trust credentials.
- `cmd_netlogon_capabilities()` returns early on `netlogon_creds_cli_check()` failure without freeing the acquired lock explicitly.
- Many commands accept numeric flags via `atoi()` or `%x` without validating semantic combinations.
- `DsrGetForestTrustInformation` and several enumeration commands print only `success`, leaving useful returned structures uninspected.
- Error handling is split between `WERROR` and `NTSTATUS`; callers must verify the command table return type when testing behavior.

## Test signals
Integration tests should exercise DC discovery with DNS and NetBIOS names, GUID parsing failures, logon-control success/failure, trust enumeration, site coverage, and secure-channel-required commands both with and without established `rpcclient_netlogon_creds`. Tests for `getanydcname` and `getdcname` should verify timeout restoration. Password and trust-password tests should run only in isolated domains where credential rotation is expected.

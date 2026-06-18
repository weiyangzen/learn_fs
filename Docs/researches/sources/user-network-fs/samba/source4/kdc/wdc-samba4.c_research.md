# sources/user-network-fs/samba/source4/kdc/wdc-samba4.c

## Purpose

`wdc-samba4.c` implements Samba's Heimdal KDC plugin table for Windows domain controller behavior. It supplies hooks for PAC generation, PAC verification/update, access policy, supported encryption type padata, referrals, and hardware-auth policy.

## Important APIs, Types, and Functions

The exported symbol is `kdc_plugin_table`. Major hooks are `samba_wdc_get_pac()`, `samba_wdc_verify_pac()`, `samba_wdc_reget_pac()`, `samba_wdc_check_client_access()`, `samba_wdc_finalize_reply()`, `samba_wdc_referral_policy()`, and `samba_wdc_hwauth_policy()`. Helpers detect S4U2Self, verify PAC signatures, extract NetBIOS workstation names, and build `PA-SUPPORTED-ENCTYPES`.

## Control Flow

PAC generation initializes a PAC, records S4U2Self and PKINIT freshness flags, gets device PAC data, calls Samba PAC glue, and attaches audit/NTSTATUS data to the request. Verification handles RODC/trust rules, fetches a signing krbtgt if needed, verifies signatures for delegated proxy cases, rejects questionable kpasswd-like near-expiry tickets, and delegates semantic PAC checks to Samba. PAC update replaces an existing PAC after refreshing groups, delegation data, and device claims. Client access first checks device policy, then account/workstation/password-change policy, and returns `KRB5_PLUGIN_NO_HANDLE` to continue Heimdal checks when allowed.

## State and Persistence Behavior

The plugin has no persistent private state. It mutates request-scoped audit info, NTSTATUS e-data, PAC contents, and policy results. Temporary talloc contexts are used per hook.

## Dependencies and Integration Points

It integrates Heimdal KDC plugin APIs, Samba KDC/HDB/SDB glue, PAC glue, auth policy utilities, generated auth NDR types, and krb5 local APIs. It is built as `WDC_SAMBA4` and linked into the Heimdal KDC service.

## Risks and Edge Cases

PAC validation is security-critical, especially RODC-issued PACs, delegated proxy tickets, checksum-enctype key selection, trust tickets, and S4U paths. `samba_wdc_reget_pac()` has an early `return EINVAL` after allocating `mem_ctx` when delegated proxy data is inconsistent. The TGT/kpasswd lifetime heuristic can reject tickets close to expiry.

## Test Signals

Coverage should include AS-REQ PAC generation, PKINIT freshness, S4U2Self, S4U2Proxy, RODC and writable DC PAC signatures, device claims, smart-card-required policy, trust TGTs, near-expiry tickets, and canonicalize replies with supported encryption types.

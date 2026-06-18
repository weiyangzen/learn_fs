## sources/user-network-fs/samba/source4/kdc/mit-kdb/kdb_samba_policies.c

Purpose: MIT KDB policy, PAC issue/update, delegation, and AS audit callbacks for Samba.

Important APIs and functions: `kdb_samba_db_check_policy_as()` rejects invalid kadmin clients, detects changepw AS requests, extracts NetBIOS workstation addresses, and calls `mit_samba_check_client_access()`, decoding returned e-data into MIT padata. `kdb_samba_db_issue_pac()` decides whether to generate a fresh PAC (`ks_get_pac`) or update/copy an old PAC (`ks_update_pac`), especially for protocol transition/cross-realm cases. `kdb_samba_db_check_allowed_to_delegate()` and `kdb_samba_db_allowed_to_delegate_from()` bridge constrained delegation checks. `kdb_samba_db_audit_as_req()` updates bad-password counters on success/preauth failure/bad integrity.

Control flow: AS policy prefers canonical client entry principal; `kadmin/*` as a client is denied. Changepw detection requires server principal `kadmin/changepw` in the default realm. PAC issue logs AS versus TGS paths and uses Samba PAC glue. Audit ignores NULL clients to avoid known FAST crash cases.

State and persistence: client access checks may set reject status on `samba_kdc_entry`; audit calls persist bad password count or success accounting through DSDB/SAMDB.

Dependencies and integration: sits between MIT KDC DAL callbacks and `mit_samba.c`, `pac-glue.c`, auth_sam accounting, and generated krb5 padata encoding/decoding.

Risks: padata decode uses an exported but undeclared MIT function. Cross-realm/protocol-transition PAC decisions are subtle and security-sensitive. Bad-password accounting only handles selected errors.

Test signals: AS login policy errors with e-data, NetBIOS address handling, password-change AS requests, S4U2Self/S4U2Proxy PAC issue paths, constrained delegation denial, and bad-password counter transitions.

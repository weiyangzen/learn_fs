## sources/user-network-fs/samba/source4/kdc/mit_kdc_irpc.c

Purpose: IRPC service support for MIT KDC PAC validation requests, primarily Netlogon generic Kerberos PAC validation.

Important APIs and functions: `samba_setup_mit_kdc_irpc()` allocates `mit_kdc_irpc_context`, creates a Samba KDC DB context and krb5 context, registers `KDC_CHECK_GENERIC_KERBEROS` with `IRPC_REGISTER()`, and advertises the `kdc_server` messaging name. `netr_samlogon_generic_logon()` parses `PAC_Validate`, fetches local krbtgt keys from Samba DB, and brute-force checks the supplied PAC checksum/signature with `check_pac_checksum()`.

Control flow: unsupported generic message types and malformed checksum/signature lengths return invalid parameter. krbtgt principal lookup failures return logon failure. Checksum verification succeeds if any krbtgt key validates the KDC signature.

State and persistence: no durable writes. It reads krbtgt keys from DSDB and updates the DB current time opaque before fetches for gMSA/time-sensitive logic.

Dependencies and integration: used by Samba process messaging/IRPC, Netlogon PAC validation NDR, `samba_kdc_fetch()`, gMSA current time, and krb5 principal creation.

Risks: signature-length validation is security critical. MIT lacks a checksum-to-enctype helper, so the brute-force key loop must stay correct and efficient. Only PAC validation is implemented; certificate validation is explicitly unsupported.

Test signals: valid and invalid PAC validation IRPC messages, malformed length combinations, multiple krbtgt enctypes, missing krbtgt, unsupported message type, and registration under `kdc_server`.

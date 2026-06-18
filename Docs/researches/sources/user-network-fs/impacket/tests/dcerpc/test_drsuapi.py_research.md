# sources/user-network-fs/impacket/tests/dcerpc/test_drsuapi.py

Purpose: validates Directory Replication Service Remote Protocol bindings and selected Active Directory replication/name service requests.

Important APIs and functions: `DRSRTests` uses `drsuapi.MSRPC_UUID_DRSUAPI`, `\PIPE\lsass`, and packet privacy. `bind()` builds `DRSBind` with `DRS_EXTENSIONS_INT`, handles replication epoch mismatch by rebinding, then retrieves the NTDS DSA object GUID with `hDRSDomainControllerInfo`. Tests cover raw/helper `DRSDomainControllerInfo`, raw/helper `DRSCrackNames`, `DRSGetNT4ChangeLog`, `DRSVerifyNames`, and xfailed `DRSGetNCChanges` v8/v10 paths. `getMoreData()` loops multi-response NC-change replies.

Control flow: most tests connect, call `bind()`, then issue one DRS request. Name-cracking tests translate Administrator and NTDS Settings names between NT4, UPN, SID, FQDN 1779, unique-id, and role formats. NC-change tests build DSNAME structures, USN vectors, partial attribute sets with schema OIDs, prefix tables, flags such as `DRS_INIT_SYNC`, and secret-replication extended ops.

State and persistence behavior: normal tests are read-only directory queries. Xfailed NC-change tests request replication data and include secret attributes (`unicodePwd`, password history, supplemental credentials), making them sensitive even if expected to fail or require privilege. No directory writes are performed.

Dependencies and integration points: depends on Active Directory domain configuration, LSASS DRSUAPI endpoint, packet privacy, and domain naming assumptions using `self.domain.split('.')`. Runs over SMB named pipe and TCP endpoint-mapped transports, in NDR and NDR64.

Risks: tests can expose sensitive replication behavior; they require domain controller privileges and can fail due to AD version, topology, or hardening. `getMoreData()` appears to assign `uuidInvocIdSrc` incorrectly from the whole V6 response object rather than a GUID field, so the xfailed loop is fragile. Hardcoded names like `DC1-WIN2012` reduce portability.

Test signals: validates DRS extension negotiation, epoch handling, domain controller info levels, name cracking, verify-name marshalling, and partially documents replication request construction.
